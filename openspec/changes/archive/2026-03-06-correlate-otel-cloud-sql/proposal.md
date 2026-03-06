## Why

Backend traces reach Cloud Trace via the OTel Collector (see `otel-collector-deployment` spec), and Cloud SQL Query Insights independently generates execution-plan spans for SQL queries. These two trace streams are disconnected — they have different Trace IDs and cannot be correlated. This makes it impossible to trace a slow RPC call down to the specific SQL execution plan that caused the latency.

## What Changes

- Introduce a `TracedPool` wrapper around `*pgxpool.Pool` that transparently instruments all database calls
- Create OTel child spans for every `Query`, `QueryRow`, `Exec`, and `Begin` call, capturing SQL text and duration
- Inject `traceparent` as a SQL comment in [sqlcommenter](https://google.github.io/sqlcommenter/) format before each query, enabling Cloud SQL Query Insights to link its execution-plan spans to the same trace
- Replace the concrete `*pgxpool.Pool` field in the `Database` struct with the wrapped pool so all repositories are instrumented without code changes

## Capabilities

### New Capabilities

- `db-trace-correlation`: End-to-end trace correlation from backend RPC spans through database query spans to Cloud SQL Query Insights execution-plan spans, using pgxpool wrapper with OTel span creation and sqlcommenter traceparent injection.

### Modified Capabilities

(none)

## Impact

- **backend** repo: New `TracedPool` wrapper in infrastructure/database layer; `Database` struct field type changes from `*pgxpool.Pool` to `*TracedPool`; no repository code changes required
- **Dependencies**: No new external dependencies — uses `go.opentelemetry.io/otel` (already in go.mod)
- **Cloud SQL**: Query Insights must be enabled on the Cloud SQL instance (already enabled per `database` spec)
- **Observability**: Cloud Trace will show a complete span tree: RPC → DB query → SQL execution plan
