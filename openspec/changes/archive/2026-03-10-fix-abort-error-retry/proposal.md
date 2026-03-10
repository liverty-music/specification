## Why

The `getFollowedArtistsWithRetry()` method in `loading-sequence-service.ts` does not distinguish cancellation errors (AbortError / ConnectError with Code.Canceled) from retriable network errors. When the 10-second global timeout fires and aborts in-flight requests, the catch block treats AbortError as a retriable failure — incrementing the retry counter, emitting misleading "Retrying" log messages, and calling `delay()` with an already-aborted signal (which throws immediately). This creates a fast retry loop that burns through all retries before the error finally propagates, wasting resources and polluting logs.

## What Changes

- Add an early-return guard in the `getFollowedArtistsWithRetry()` catch block that immediately re-throws cancellation errors without retrying
- The guard must detect both `AbortError` (from raw `fetch()` / `delay()`) and `ConnectError` with `Code.Canceled` (from Connect-RPC transport)
- Follow the existing codebase pattern for AbortError detection: `(err as Error).name === 'AbortError'`

## Capabilities

### New Capabilities

_None — this is a bug fix within existing capabilities._

### Modified Capabilities

- `loading-sequence`: The "Initial artist list retrieval failure" scenario's retry behavior is refined to exclude intentional cancellation from retriable errors. The spec currently says "the ListFollowedArtists RPC fails after retries" but does not specify that cancellation (abort) should bypass retries entirely.

## Impact

- **Code**: `frontend/src/services/loading-sequence-service.ts` — `getFollowedArtistsWithRetry()` catch block (~line 115-126)
- **Dependencies**: Requires `ConnectError` and `Code` imports from `@connectrpc/connect`
- **Behavior**: AbortError and Canceled errors now propagate immediately instead of being retried, resulting in faster cleanup when the global timeout fires
- **Logs**: Eliminates false "Retrying followed artists fetch" log entries during intentional cancellation
- **Risk**: Low — the fix only adds an early-exit path; all other error handling remains unchanged
