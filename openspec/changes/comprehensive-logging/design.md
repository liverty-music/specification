## Context

The backend uses `slog` via a custom wrapper (`github.com/pannpers/go-logging/logging`) with configurable level/format via `LOGGING_LEVEL` and `LOGGING_FORMAT` environment variables. An access log interceptor exists at the Connect-RPC transport level. The frontend uses Aurelia 2's `ILogger` with `ConsoleSink` and `OtelLogSink`, plus an OTEL interceptor for RPC spans. Despite this infrastructure being in place, most application-level code lacks structured logging — particularly blockchain interactions, external API calls, and database mutations on the backend, and fire-and-forget mutations on the frontend.

## Goals / Non-Goals

**Goals:**
- Achieve operational visibility into all blockchain, external API, and database mutation operations
- Enable effective troubleshooting with context attributes (userID, artistID, eventID, etc.)
- Provide appropriate log levels: INFO for data mutations and key business logic, DEBUG for development/troubleshooting, WARN for non-fatal anomalies, ERROR for failures
- Add frontend RPC logging interceptor for unified request/response tracing
- Make fire-and-forget RPC failures visible to users via toast + 1-retry

**Non-Goals:**
- Changing the logging library or infrastructure (slog stays, ILogger stays)
- Adding request-scoped correlation IDs or distributed tracing enhancements (covered by existing OTEL)
- Adding logging to read-only database queries (SELECT)
- Modifying the access log interceptor format
- Adding metrics or dashboards

## Decisions

### D1: Log levels by operation type

| Operation | Level | Rationale |
|-----------|-------|-----------|
| Data mutations (INSERT/UPDATE, mint, follow) | INFO | Business-critical state changes must always be visible |
| External API requests (outbound) | INFO | Operational visibility for third-party dependencies |
| Entry verification steps | INFO | Security-relevant audit trail |
| Retry attempts (blockchain, API) | DEBUG | High volume during failures; needed for troubleshooting only |
| Rate limiter backoff | DEBUG | Useful for diagnosing latency, not needed in normal operation |
| Constraint violations (duplicate key) | WARN | Expected but noteworthy condition |
| Token existence check edge cases | WARN | Reconciliation scenarios need developer attention |
| All failures | ERROR | Standard |

**Alternative considered**: Making all external API calls DEBUG-level. Rejected because third-party failures are a primary source of production incidents and must be visible by default.

### D2: Backend — inject logger via existing DI, scope per component

Each infrastructure client and repository will receive `*slog.Logger` through the existing `di/provider.go` injection. Logger will be scoped with `.With()` at construction time to include the component name (e.g., `slog.String("component", "lastfm")`).

**Alternative considered**: Using a middleware/interceptor pattern for external API logging. Rejected because each client has different context attributes and error handling patterns that benefit from explicit logging.

### D3: Backend — context attributes per operation

Each log statement will include relevant business context as slog attributes:

- Blockchain: `tokenID`, `userID`, `eventID`, `attempt`, `maxAttempts`, `txHash` (on success)
- External APIs: `artistID`, `venueID`, `query`, `statusCode`
- Database mutations: `entityType`, `entityID`, `userID`
- Entry verification: `eventID`, `userID`, `step` (merkle/nullifier/eventID)
- On-chain errors: include response body as `responseBody` attribute

### D4: Frontend — Connect-RPC logging interceptor

Add a new interceptor to the existing interceptor chain in `grpc-transport.ts`:

```
Interceptor chain: [otelInterceptor, loggingInterceptor, authInterceptor]
```

The logging interceptor will:
- Log at DEBUG on request start with method name
- Log at DEBUG on success with method name and duration (ms)
- Log at ERROR on failure with method name, duration, and Connect error code

Scoped logger: `resolve(ILogger).scopeTo('ConnectRPC')`

**Alternative considered**: Extending the existing OTEL interceptor. Rejected because OTEL spans serve a different purpose (distributed tracing) than application-level logging (developer console output, log aggregation).

### D5: Frontend — fire-and-forget retry with toast

For fire-and-forget RPC calls (unfollow artist, update passion level):

1. On first failure: immediately retry once
2. If retry also fails: show toast via `IToastService.show()` and revert optimistic UI
3. Log at ERROR with operation details

Pattern:
```
try {
  await rpcCall()
} catch (firstErr) {
  logger.warn('RPC failed, retrying', { method, firstErr })
  try {
    await rpcCall()
  } catch (retryErr) {
    logger.error('RPC retry failed', { method, retryErr })
    toastService.show('Operation failed. Please try again.')
    revertOptimisticUpdate()
  }
}
```

### D6: Frontend — replace console.* with ILogger

Two specific locations:
- `grpc-transport.ts:33`: `console.error` → Requires creating a scoped logger available in the transport factory function. Pass `ILogger` as parameter to `createTransport()`.
- `main.ts:72-74`: `console.warn` → Use the app-level logger already available in the startup context.

### D7: Backend — on-chain communication body logging

For blockchain RPC calls (`ticketsbt/client.go`):
- Log response body on ERROR (mint failure, owner query failure)
- Log transaction hash on successful mint at INFO level
- Do not log response body on success for routine queries (OwnerOf, IsTokenMinted)

## Risks / Trade-offs

- **[Log volume increase]** → Mitigated by using DEBUG for high-frequency operations (retries, rate limiting) and INFO only for state changes. Production default `LOGGING_LEVEL=info` keeps volume manageable.
- **[Sensitive data in logs]** → Mitigated by logging IDs (userID, artistID) not PII (email, name). Blockchain private keys are never logged. API keys are never included in attributes.
- **[Performance impact of logging in hot paths]** → slog is lazy-evaluated; DEBUG calls are no-ops when level is INFO. Frontend ILogger similarly skips below-threshold levels.
- **[Frontend retry may cause duplicate mutations]** → Mitigated by backend idempotency checks already in place for follow/unfollow operations. Passion level update is also idempotent (last-write-wins).
