## Why

The `SearchNewConcerts` RPC consistently times out in dev because the global HTTP handler timeout (`SERVER_HANDLER_TIMEOUT=5s`) is too short for Gemini API calls that use Google Search grounding. Gemini typically takes 2–5 seconds to respond, and under load it exceeds the 5s deadline, returning `DEADLINE_EXCEEDED` (504). The frontend does not set a `timeoutMs` on the RPC call, so the server's conservative 5s insurance timeout is the only deadline — and it's too short.

## What Changes

- **Frontend**: Set `timeoutMs: 20000` on `searchNewConcerts` RPC calls so the client explicitly declares how long it's willing to wait
- **Backend**: Increase `SERVER_HANDLER_TIMEOUT` from 5s to 30s as an insurance safety net (the client's `timeoutMs` is the primary deadline)
- **Backend**: Add retry logic with exponential backoff to the Gemini API caller so transient timeouts are retried automatically

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this is a client timeout + infrastructure resilience fix with no spec-level behavior change)

## Impact

- **Frontend**: `src/services/concert-service.ts` (add `timeoutMs`), `src/services/artist-discovery-service.ts` (pass through timeout), `src/services/loading-sequence-service.ts` (pass through timeout)
- **Backend**: `internal/infrastructure/gcp/gemini/searcher.go` (retry logic), `pkg/config/config.go` (`SERVER_HANDLER_TIMEOUT` default change)
- **Risk**: Low — fire-and-forget pattern means frontend is already resilient to failures; this improves success rate
