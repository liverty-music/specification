## Context

The backend uses `*pgxpool.Pool` directly in all repository implementations (`r.db.Pool.Query(ctx, sql, args...)`). OTel tracing is configured at the RPC layer (Connect-RPC `otelconnect` interceptor) and messaging layer (Watermill OTel middleware), but no instrumentation exists at the database query layer.

Cloud SQL Query Insights is enabled and generates execution-plan spans (Seq Scan, Hash Join, etc.), but these are isolated — no `traceparent` is propagated from the application to Cloud SQL.

pgx v5.8.0 (latest) provides a `QueryTracer` interface on `ConnConfig`, but it cannot modify SQL text — `TraceQueryStartData.SQL` is read-only. The `QueryRewriter` interface can rewrite SQL but must be passed as an argument to each query call, requiring changes to every repository method.

## Goals / Non-Goals

**Goals:**

- Create OTel spans for all database queries (Query, QueryRow, Exec) with SQL text and duration
- Inject `traceparent` in sqlcommenter format so Cloud SQL Query Insights correlates its spans with the backend trace
- Zero changes to repository code — instrumentation is transparent via pool wrapper
- Support transactions (`Begin`) with trace context propagation

**Non-Goals:**

- Tracing `CopyFrom` or `SendBatch` operations (not used in this codebase)
- Adding non-traceparent sqlcommenter fields (route, controller, framework) — can be added later
- Configurable sampler for DB spans — follows the global `AlwaysSample` policy
- Metrics collection (connection pool stats, query counts) — separate concern

## Decisions

### Decision 1: Pool wrapper vs. pgx Tracer interface

**Chosen: Pool wrapper (`TracedPool` struct)**

Alternatives considered:

| Approach | Span creation | SQL comment injection | Repo changes |
|----------|--------------|----------------------|--------------|
| **A. Pool wrapper** | Yes (in wrapper) | Yes (in wrapper) | None |
| B. pgx `QueryTracer` | Yes | No (SQL is read-only) | None |
| C. pgx `QueryRewriter` | No | Yes | Every query call |
| D. B + C combined | Yes | Yes | Every query call |
| E. `otelpgx` library | Yes | No | None |
| F. Switch to `database/sql` + `otelsql` | Yes | Yes (`WithSQLCommenter`) | Full rewrite |

Rationale: Only the wrapper approach achieves both goals without touching repository code. The wrapper intercepts `Query`/`QueryRow`/`Exec`/`Begin` calls, prepends the sqlcommenter comment to the SQL string, creates an OTel span, delegates to the inner `*pgxpool.Pool`, and ends the span.

### Decision 2: Interface vs. concrete wrapper type

**Chosen: Concrete `*TracedPool` struct**

The `Database.Pool` field changes from `*pgxpool.Pool` to `*TracedPool`. The wrapper exposes the same method signatures as `*pgxpool.Pool` for the methods used by repositories (`Query`, `QueryRow`, `Exec`, `Begin`, `Ping`, `Close`).

An interface was considered but rejected: the codebase accesses `r.db.Pool` directly and only uses a fixed set of methods. A concrete type is simpler and avoids introducing a new interface that would need to be maintained. If testing requires a mock pool in the future, an interface can be extracted then.

### Decision 3: SQL comment format and placement

**Chosen: Prepend `/*traceparent='...'*/` before SQL text**

Format follows the [sqlcommenter specification](https://google.github.io/sqlcommenter/spec/):

```sql
/*traceparent='00-{32hex_trace_id}-{16hex_span_id}-{2hex_flags}'*/ SELECT ...
```

- Comment is prepended (not appended) — Cloud SQL Query Insights parses both positions, but prepending is the sqlcommenter convention
- Only `traceparent` key is included — minimal and sufficient for trace correlation
- Values are URL-encoded per spec (traceparent uses only hex chars, so no encoding needed in practice)
- Keys are sorted alphabetically (trivial with a single key)

### Decision 4: Span attributes and naming

Spans follow [OTel semantic conventions for database](https://opentelemetry.io/docs/specs/semconv/database/):

- **Span name**: SQL operation extracted from the first keyword (e.g., `SELECT`, `INSERT`, `UPDATE`, `DELETE`), or `DB` as fallback
- **`db.system`**: `postgresql`
- **`db.query.text`**: Full SQL text (without the injected comment)
- **`db.operation.name`**: Extracted operation (SELECT, INSERT, etc.)
- **Span kind**: `Client`

### Decision 5: Transaction tracing

`Begin` returns a `pgx.Tx`. The wrapper creates a span for the `Begin` call itself, but individual queries within the transaction are executed through `pgx.Tx` methods — not through the pool wrapper.

To trace queries within transactions, the wrapper returns a `TracedTx` that wraps `pgx.Tx` with the same span creation and comment injection logic.

### Decision 6: File placement

`TracedPool` lives in `internal/infrastructure/database/rdb/` alongside `postgres.go`, as it is tightly coupled to the database infrastructure layer. It is not a general-purpose telemetry utility — it specifically wraps pgxpool for this codebase's needs.

## Risks / Trade-offs

**[SQL comment adds bytes to every query]** → The traceparent comment is ~80 bytes. Negligible compared to typical query sizes. Cloud SQL's `max_query_length` for Query Insights defaults to 10KB, so the comment will not cause truncation.

**[Span overhead on every DB call]** → Each span adds ~1-2μs of overhead (context propagation + span creation). With AlwaysSample, every query creates a span. This is acceptable for the current scale. If span volume becomes a concern, a DB-specific sampler can be added later.

**[TracedTx wrapping complexity]** → `pgx.Tx` has methods like `Query`, `QueryRow`, `Exec`, `Commit`, `Rollback`, `CopyFrom`, `SendBatch`. We only wrap the methods actually used in the codebase. If new `pgx.Tx` methods are used in the future, they'll need to be added to `TracedTx`.

**[No span for pool acquisition wait time]** → The wrapper creates a span that includes both pool acquisition and query execution time. Separating these would require using `pgxpool.AcquireTracer`, which adds complexity without clear immediate value.
