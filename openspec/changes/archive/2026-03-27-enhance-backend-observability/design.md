## Context

The backend service (Go, Connect-RPC) currently has two instrumentation layers:

1. **RPC layer**: `otelconnect` interceptor auto-creates spans for every Connect-RPC call
2. **Database layer**: Custom `TracedPool`/`TracedTx` wrappers create client spans for every SQL query with sqlcommenter traceparent injection

Between these two layers, all business logic (usecases, external API calls, event publishing) is invisible. The SDK uses `AlwaysSample()` globally and has no Metrics signal. Six external HTTP clients pass `nil` for `*http.Client` in production, bypassing any transport-level instrumentation.

## Goals / Non-Goals

**Goals:**
- Full visibility into request latency breakdown: RPC → external API → business logic → DB
- Metrics signal for operational alerting (latency histograms, error counters, pool gauges)
- Production-safe sampling with environment-aware configuration
- DB span compliance with OTel Semantic Conventions

**Non-Goals:**
- OTel Collector metrics pipeline configuration (cloud-provisioning scope)
- Log-Trace correlation (already handled by `go-logging`)
- Tier 3 instrumentation (cache hit/miss, rate limiter waits, background goroutines)
- Frontend or consumer-specific observability beyond what flows through shared telemetry setup
- Custom dashboards or alerting rules

## Decisions

### D1: External HTTP client instrumentation via `otelhttp.NewTransport()`

**Decision**: Wrap each external HTTP client's transport with `otelhttp.NewTransport()` at the DI layer, rather than adding manual span creation inside each client.

**Why**: Transport-level wrapping captures all HTTP calls uniformly (method, URL, status code, duration) without modifying client internals. Each client already accepts `*http.Client` — the DI layer just needs to construct it with an instrumented transport.

**Client-specific patterns**:

| Client | Transport Chain | Auth Handling |
|--------|----------------|---------------|
| Gemini (genai) | `DefaultTransport → otelhttp → authTransport` | `ClientConfig.UseDefaultCredentials()` layers ADC on top of provided HTTPClient |
| Google Maps | `DefaultTransport → otelhttp → RetryTransport` | Manual `TokenSource` injection in request headers (unchanged) |
| Last.fm | `DefaultTransport → otelhttp` | API key in query params (unchanged) |
| MusicBrainz | `DefaultTransport → otelhttp` | User-Agent header (unchanged) |
| fanart.tv / Logo Fetcher | `DefaultTransport → otelhttp` | API key in header (unchanged) |

**Alternative considered**: Using per-method `tracer.Start()` inside each client. Rejected because it duplicates HTTP-level attributes that `otelhttp` captures automatically and requires changes to every client method.

### D2: Gemini ADC integration with `UseDefaultCredentials()`

**Decision**: Construct `genai.ClientConfig` with an `otelhttp`-wrapped `*http.Client`, then call `cc.UseDefaultCredentials()` to layer ADC authentication on top.

**Why**: `UseDefaultCredentials()` (available since genai v1.34.0, current: v1.44.0) wraps whatever transport the provided HTTPClient has with an `authTransport`. This means:
- `otelhttp` sees requests **before** auth headers are added (no credential leakage in span attributes)
- ADC token refresh is handled transparently
- Test code continues to pass custom `*http.Client` without calling `UseDefaultCredentials()`

**Alternative considered**: `httptransport.AddAuthorizationMiddleware()` for manual credential setup. Rejected because `UseDefaultCredentials()` is simpler and officially supported by the genai SDK.

### D3: Zitadel gRPC instrumentation via `otelgrpc` interceptors

**Decision**: Pass `otelgrpc` unary and stream interceptors as gRPC dial options to the Zitadel client.

**Why**: Zitadel uses gRPC (not HTTP). The `zitadel-go/v3` library accepts `zitadelconn.Option` which wraps gRPC dial options. Adding `grpc.WithStatsHandler(otelgrpc.NewClientHandler())` instruments all gRPC calls uniformly.

### D4: UseCase spans limited to CPU-intensive logic only

**Decision**: Add spans to exactly 3 methods where in-process computation is the primary time cost:

1. **`BuildMerkleTree()`**: Cryptographic identity commitment (hash per ticket) + O(n log n) tree construction
2. **`executeSearch()` → `FilterNew`**: O(n) deduplication with date comparisons and set construction
3. **`persistArtists()`**: 5-pass map/array manipulation (collect MBIDs → build existing set → determine missing → batch create → merge preserving order)

**Why**: After Phase 2 wraps all external API and DB calls with spans, only CPU-bound processing remains invisible. Adding spans to methods where external calls dominate (e.g., `MintTicket`, `VerifyEntry`, `CreateFromDiscovered`) would add noise without diagnostic value.

### D5: `SetupTelemetry` expanded to `SetupObservability`

**Decision**: Expand `pkg/telemetry/telemetry.go` to initialize both `TracerProvider` and `MeterProvider`, and return a unified closer that shuts down both.

**Configuration additions to `TelemetryConfig`**:
- `SamplerRatio float64` (`TELEMETRY_SAMPLER_RATIO`, default: `1.0`) — used with `ParentBased(TraceIDRatioBased(ratio))`
- `Environment` derived from existing `BaseConfig.Environment`

**Resource attributes added**:
- `deployment.environment` (from `BaseConfig.Environment`)

**Propagator**: Explicitly set `otel.SetTextMapPropagator(propagation.TraceContext{})` instead of relying on defaults.

**Why unified**: Traces and metrics share the same resource, OTLP endpoint, and shutdown lifecycle. A single setup function avoids divergent configuration.

### D6: Metrics instrument selection

**Decision**: Introduce metrics incrementally, starting with the highest-signal instruments:

| Instrument | Type | Purpose |
|------------|------|---------|
| `rpc.server.request.duration` | Histogram | RPC latency distribution (already captured by otelconnect — verify) |
| `external_api.request.duration` | Histogram | External API call latency by service |
| `external_api.request.total` | Counter | External API call count by service and status |
| `blockchain.mint.duration` | Histogram | Ticket minting latency |
| `blockchain.mint.total` | Counter | Mint count by outcome (success, retry, failure) |
| `db.pool.active_connections` | ObservableGauge | pgxpool active connections (from `pool.Stat()`) |
| `db.pool.idle_connections` | ObservableGauge | pgxpool idle connections |

**Why these first**: RPC and external API durations surface the top latency contributors. Blockchain metrics catch mint failures. Pool gauges catch connection exhaustion. All can trigger alerts without building custom dashboards.

**Alternative considered**: Full RED metrics (Rate, Errors, Duration) for every component. Rejected for initial scope — start with high-signal instruments and expand based on operational need.

### D7: DB span Semantic Convention enrichment

**Decision**: Add missing attributes to `TracedPool.startSpan()` and `TracedTx.startSpan()`:

| Attribute | Source |
|-----------|--------|
| `db.collection.name` | Extract table name from SQL (after FROM/INTO/UPDATE/JOIN) |
| `db.namespace` | From `DatabaseConfig` (database name), passed to `TracedPool` at construction |
| `server.address` | From `DatabaseConfig.Host`, passed to `TracedPool` at construction |
| `db.response.status_code` | Extract PG error code from `*pgconn.PgError` in `recordError()` |

**Why**: These are conditionally required by OTel DB Semantic Conventions. `db.collection.name` enables filtering traces by table. `db.response.status_code` distinguishes constraint violations from connection errors.

**Table name extraction**: Extend the existing `ExtractOperation()` function to also return the table name. Use a simple regex for common patterns (`FROM \w+`, `INTO \w+`, `UPDATE \w+`). Complex queries (CTEs, subqueries) may not match — that is acceptable as `db.collection.name` is optional.

### D8: Context propagation fix in ConcertUseCase

**Decision**: Replace `context.Background()` with `context.WithoutCancel(ctx)` in `markSearchCompleted()` and `markSearchFailed()`.

**Why**: The design intent is to detach from the parent's deadline/cancellation (the search may time out but the status update must still run). `context.WithoutCancel(ctx)` preserves the trace context (trace_id, span_id) while removing the cancellation signal — exactly the needed semantics.

## Risks / Trade-offs

**[Span volume increase] → Mitigation: Sampler ratio**
Adding otelhttp spans for all external API calls increases span volume significantly. The `ParentBased(TraceIDRatioBased)` sampler ensures only a configured percentage of traces are sampled in production. Development keeps `AlwaysSample()` via ratio `1.0`.

**[Table name extraction fragility] → Mitigation: Graceful fallback**
SQL parsing for `db.collection.name` uses simple regex, not a full SQL parser. Complex queries (CTEs, dynamic SQL) may not match. The attribute is simply omitted when extraction fails — no error, no incorrect data.

**[Gemini UseDefaultCredentials() coupling] → Mitigation: Version pin awareness**
`UseDefaultCredentials()` was added in genai v1.34.0. If the genai library is downgraded below this version, compilation fails immediately (not a silent regression). Current version is v1.44.0 with significant margin.

**[Metrics exporter requires Collector pipeline] → Mitigation: Conditional export**
Same pattern as traces: metrics exporter is only created when `OTLPEndpoint` is configured. Local development without a Collector runs without exporting metrics.
