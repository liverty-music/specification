## Context

External API clients handle transient errors inconsistently:

| Client | Throttle | Retry on Rate Limit | Retry on Transient |
|--------|----------|--------------------|--------------------|
| Last.fm | 200ms (in-memory) | No | No |
| MusicBrainz | 1s (in-memory) | No | No |
| Google Maps | None | No | No |
| Gemini | N/A (SDK) | Yes (hand-rolled) | Yes (hand-rolled) |
| Blockchain | N/A (RPC) | N/A | Yes (hand-rolled) |

In-memory throttling breaks when multiple K8s pods or concurrent consumers/jobs overlap. When rate limits are hit, there is no retry — the error propagates immediately. Gemini and Blockchain have duplicated inline retry loops.

## Goals / Non-Goals

**Goals:**
- Provide a reusable HTTP retry mechanism via `http.RoundTripper` wrapper in `pkg/httpx`
- Retry on transient HTTP errors (429, 503, 504) with exponential backoff and jitter
- Respect `Retry-After` headers from upstream APIs
- Unify Gemini's hand-rolled retry to use `cenkalti/backoff/v5`
- Maintain the existing throttle → request flow with correct ordering

**Non-Goals:**
- Circuit breaker pattern (not needed at current scale)
- Per-client rate limit quotas or distributed throttling (future work)
- Modifying the Blockchain RPC retry (not HTTP-based, different protocol)
- Adding retry to WebPush sender (fire-and-forget by design)
- Changing error codes returned to callers (existing `api.FromHTTP` mapping stays)

## Decisions

### 1. Library: `cenkalti/backoff/v5`

Already an indirect dependency in `go.mod`. Promotes to direct usage.

**Why not alternatives:**
- `hashicorp/go-retryablehttp` — HTTP-only; cannot reuse for Gemini SDK. Would add a second retry path.
- `sethvargo/go-retry` — No `Retry-After` support. Lower adoption (708 stars vs 4,000+).
- `failsafe-go` — Over-engineered for current needs (circuit breaker, hedging). Larger dependency.
- Custom implementation — Duplicates what `cenkalti/backoff` already provides well.

### 2. Package placement: `pkg/httpx`

New package `pkg/httpx` containing a `RetryTransport` that implements `http.RoundTripper`.

**Why `pkg/httpx`:**
- `pkg/` is for reusable, domain-agnostic utilities (same as `pkg/throttle`, `pkg/api`)
- `httpx` follows Go convention for stdlib extensions (`sqlx`, `netx`)
- Keeps `pkg/api` focused on error conversion only

**Why not `internal/infrastructure/`:**
- Retry is not an adapter/driver; it's a transport-layer concern
- Multiple infrastructure clients share it — it belongs in the shared utility layer

### 3. Retry scope: transient HTTP status codes only

Retryable status codes: **429** (Too Many Requests), **503** (Service Unavailable), **504** (Gateway Timeout).

Non-retryable: all 4xx (except 429), 501, connection errors without response.

`Retry-After` header is parsed when present (both absolute date and delta-seconds formats) and used as the minimum backoff for that attempt.

### 4. Throttle-retry ordering: retry outside throttle (Pattern A)

```
retry loop (with backoff) {
    throttle.Do {
        httpClient.Do(req)   ← plain Transport, no RetryTransport
    }
}
```

**Why not RoundTripper-based retry for throttled clients:**
- If retry lives inside `RoundTripper`, the backoff wait blocks the throttle slot
- Other callers waiting in the throttle queue are starved during backoff
- Pattern A releases the throttle slot immediately on failure, backs off externally, then re-enters the queue

**Implementation:** For Last.fm and MusicBrainz, introduce a `retryDo` helper in each client's `get` method that wraps the existing `throttler.Do` call with `backoff.Retry`. The `RetryTransport` is used only by clients without a throttler (Google Maps).

### 5. Gemini: replace inline retry with `backoff.Retry`

Gemini uses the `genai` SDK (not raw HTTP), so `RetryTransport` cannot be used. Instead, wrap the `GenerateContent` call with `backoff.Retry()` using the existing `isRetryable()` predicate.

This replaces the hand-rolled `for attempt := range maxAttempts` loop while preserving identical behavior: max 3 attempts, exponential backoff, context cancellation.

### 6. Configuration defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| Max retries | 3 | Matches existing Gemini/Blockchain patterns |
| Initial interval | 1s | Conservative; avoids hammering rate-limited APIs |
| Max interval | 10s | Cap for exponential growth |
| Multiplier | 2.0 | Standard exponential doubling |
| Jitter | Full (randomized) | Prevents thundering herd across pods |

Configurable via functional options on `RetryTransport` and passed through DI.

## Risks / Trade-offs

**[Risk] Retry amplifies load during outage** → Mitigated by max retry cap (3), exponential backoff with jitter, and `Retry-After` header respect. At scale, circuit breaker would be the next step.

**[Risk] Throttle + retry interaction complexity** → Two distinct patterns (RoundTripper for non-throttled, explicit retry loop for throttled) may confuse future developers. → Mitigated by clear doc comments explaining the pattern choice and a code comment at each usage site.

**[Risk] Request body replay for POST requests** → Google Maps uses POST. `http.Request.Body` is consumed on first read. → `RetryTransport` must buffer or use `GetBody` to replay the body. `http.NewRequest` sets `GetBody` automatically for `bytes.Reader` and `strings.Reader`, which covers our usage.

**[Trade-off] Not unifying Blockchain retry** → Blockchain uses `go-ethereum` RPC client, not HTTP. Forcing it through the same pattern would add complexity without benefit. Its existing retry loop is adequate.
