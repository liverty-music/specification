## Context

The `loading-sequence-service.ts` orchestrates data aggregation with a 10-second global timeout using `AbortController`. When the timeout fires, in-flight requests are aborted. The `getFollowedArtistsWithRetry()` method catches all errors uniformly and retries up to `maxRetries` times, but does not check whether the error represents intentional cancellation.

Two distinct error types represent cancellation in this codebase:
1. **`AbortError`** — thrown by `fetch()` and by `delay()` when its signal is aborted
2. **`ConnectError` with `Code.Canceled`** — thrown by the Connect-RPC transport when the underlying fetch is aborted

The existing transport-level `createRetryInterceptor` already excludes `Code.Canceled` from retries, but the application-level retry in `getFollowedArtistsWithRetry()` has no such guard.

## Goals / Non-Goals

**Goals:**
- Immediately propagate cancellation errors without retrying in `getFollowedArtistsWithRetry()`
- Eliminate false "Retrying followed artists fetch" log messages during timeout-triggered abort
- Follow existing codebase conventions for error detection

**Non-Goals:**
- Refactoring the retry logic into a reusable utility (one call site only)
- Adding cancellation handling to other retry sites (no others exist currently)
- Modifying the transport-level interceptor chain

## Decisions

### Decision 1: Guard placement — early return at top of catch block

Add a cancellation check as the first statement in the catch block, before `attempt++`. This ensures no retry counter increment, no misleading log, and no `delay()` call.

**Alternative considered**: Checking after `attempt++` — rejected because it would still increment the counter and could log misleading retry messages on partial paths.

### Decision 2: Dual error type detection

Check both error types in a single guard:
```typescript
const isCanceled =
    (err instanceof Error && err.name === 'AbortError') ||
    (err instanceof ConnectError && err.code === Code.Canceled)
if (isCanceled) throw err
```

**Rationale**: The Connect-RPC transport wraps `fetch` AbortError into `ConnectError(Code.Canceled)` for RPC calls, but `delay()` throws a raw `AbortError`. Both must be handled.

**Alternative considered**: Only checking `AbortError` — rejected because the RPC call path throws `ConnectError(Code.Canceled)`, not `AbortError`.

### Decision 3: Follow existing AbortError detection pattern

Use `err instanceof Error && err.name === 'AbortError'` consistent with existing patterns in `dashboard.ts:63`, `tickets-page.ts:36,105`, and `my-artists-page.ts:125`.

**Alternative considered**: `err instanceof DOMException && err.name === 'AbortError'` — rejected because the existing codebase uses the broader `Error` check, and `delay()` throws `new Error('Aborted')` which is not a `DOMException`. Note: the `delay()` error sets `name = 'AbortError'` explicitly, so the name check works for both native and synthetic abort errors.

## Risks / Trade-offs

- **[Risk] `delay()` may not set `err.name = 'AbortError'`** → Verify the `delay()` implementation. If it throws a plain `Error('Aborted')` without setting `.name`, the guard won't catch it, and the retry loop will still execute (same as current behavior, not worse). Mitigation: check and fix `delay()` if needed to set `.name = 'AbortError'`.
- **[Risk] Future error types for cancellation** → If a new transport layer introduces a different cancellation error type, this guard would miss it. Mitigation: low risk; the Connect-RPC ecosystem is stable and the two types cover all known paths.
