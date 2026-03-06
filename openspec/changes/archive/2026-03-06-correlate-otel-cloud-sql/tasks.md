## 1. Core Implementation

- [x] 1.1 Create `TracedPool` struct in `internal/infrastructure/database/rdb/traced_pool.go` wrapping `*pgxpool.Pool` with OTel tracer, implementing `Query`, `QueryRow`, `Exec`, `Begin`, `Ping`, `Close` methods
- [x] 1.2 Implement sqlcommenter `traceparent` comment injection helper that extracts trace context from `context.Context` and formats `/*traceparent='00-{trace_id}-{span_id}-{flags}'*/`
- [x] 1.3 Implement SQL operation name extraction helper (parses first keyword: SELECT, INSERT, UPDATE, DELETE, etc.) for span naming
- [x] 1.4 Create `TracedTx` struct wrapping `pgx.Tx` with the same span creation and comment injection for `Query`, `QueryRow`, `Exec`, `Commit`, `Rollback`

## 2. Integration

- [x] 2.1 Change `Database.Pool` field type from `*pgxpool.Pool` to `*TracedPool` in `postgres.go`
- [x] 2.2 Wrap the pool with `TracedPool` in the `New` constructor after `pgxpool.NewWithConfig` returns
- [x] 2.3 Update `Ping` and `Close` methods on `Database` to delegate to `TracedPool`

## 3. Testing

- [x] 3.1 Write unit tests for sqlcommenter comment injection (with span, without span, format correctness)
- [x] 3.2 Write unit tests for SQL operation name extraction (SELECT, INSERT, UPDATE, DELETE, CTE, unknown)
- [x] 3.3 Verify existing integration tests pass with `TracedPool` (no repository code changes)
