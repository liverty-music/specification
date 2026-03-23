## Context

SearchNewConcerts RPC is now synchronous — it waits for Gemini API completion before returning a response.

Observed Gemini API response times (from production logs):

```
Successful calls:  16.5s, 17.4s, 24.6s, 24.8s, 25.0s
Failed calls:      all hit 30s timeout (HandlerTimeout)
```

Current timeout chain (lowest value wins):

```
GCP Backend Policy:  timeoutSec = 30s   ← bottleneck
HTTP HandlerTimeout: 30s                ← bottleneck
context.WithTimeout: 60s                ← redundant (HandlerTimeout sets ctx deadline)
Gemini API (actual): 16-25s per call
```

Failure pattern: Gemini returns 504 DEADLINE_EXCEEDED after ~25s → retry with 1s backoff → second call starts at ~26s → hits 30s HandlerTimeout at ~30s → deadline_exceeded.

Current pod termination chain:

```
terminationGracePeriodSeconds: 60s
├── preStop: sleep 5s
├── SHUTDOWN_TIMEOUT: 45s  ← insufficient for 60s HandlerTimeout
└── buffer: 10s
```

## Goals / Non-Goals

**Goals:**
- Unify the timeout chain at 60s so requests survive Gemini API latency
- Align pod termination chain so in-flight 60s requests can complete during shutdown
- Fail fast on Gemini 504/499 instead of wasting time on futile retries
- Eliminate redundant `context.WithTimeout` — single source of truth for request deadline

**Non-Goals:**
- Per-RPC timeout configuration (not needed at this time)
- Reducing Gemini API latency (external dependency)

## Decisions

### 1. Unify timeout at 60s (not 65s)

With `context.WithTimeout` removed from `concert_uc.go`, the HandlerTimeout IS the only deadline. No "buffer between context and handler" is needed. 60s is clean and sufficient — successful Gemini calls complete in 16-25s, leaving 35-44s margin.

### 2. Remove `context.WithTimeout(60s)` from concert_uc.go

Go best practice: the caller (HTTP handler/HandlerTimeout) sets the context deadline, callees inherit it. Adding another `context.WithTimeout` in the usecase layer is redundant and creates confusing layered timeouts. The `markSearchCompleted`/`markSearchFailed` methods already use `context.Background()` with their own timeouts (5s) for post-search DB updates, so they are unaffected.

### 3. Skip retry on Gemini 504 and 499

Remove `http.StatusGatewayTimeout` (504) and `499` from `isRetryable()` in `errors.go`.

Rationale from production logs:
- 504 DEADLINE_EXCEEDED means Gemini's own processing exceeded its internal deadline
- 499 CANCELLED means the operation was cancelled on Gemini's server side
- Retrying these wastes 15-25s per attempt with no improvement
- User can retry by tapping the bubble again

Retryable codes remain: 401 (WI token refresh), 503 (transient unavailability), 429 (rate limit).

### 4. Extend pod termination chain to accommodate 60s requests

A request in-flight when SIGTERM arrives must complete before the pod is killed:

```
Before:                                  After:
terminationGracePeriodSeconds: 60s       terminationGracePeriodSeconds: 75s
├── preStop: 5s                          ├── preStop: 5s
├── SHUTDOWN_TIMEOUT: 45s                ├── SHUTDOWN_TIMEOUT: 60s
└── buffer: 10s                          └── buffer: 10s

Shutdown formula:                        Shutdown formula:
  SHUTDOWN_TIMEOUT =                       SHUTDOWN_TIMEOUT =
    termGrace(60) - preStop(5)               termGrace(75) - preStop(5)
    - buffer(10) = 45s                       - buffer(10) = 60s
```

Without this change, a 55s request arriving just before SIGTERM would be killed at the 45s SHUTDOWN_TIMEOUT mark.

### 5. Extend global HandlerTimeout (not per-RPC)

Go's `http.Server` has a single HandlerTimeout. An alternative would be per-handler middleware, but this adds complexity for no benefit — other RPCs complete in a few hundred ms, so 60s has no practical impact on them.

## Risks / Trade-offs

- [Risk] Extended HandlerTimeout allows a buggy RPC with an infinite loop to hold resources for up to 60s → Mitigation: Only SearchNewConcerts legitimately takes this long; other RPCs return quickly. Monitor via access log `duration_ms`.
- [Risk] Extended GCP LB timeout widens the window for slow loris attacks → Mitigation: Protected by existing Cloud Armor configuration.
- [Risk] Removing 504/499 from retryable means Gemini transient failures won't be retried → Mitigation: Production data shows 504 retries never succeed within the remaining timeout. Users can retry manually. CronJob (which processes all artists weekly) has its own longer timeout and will catch missed concerts.
