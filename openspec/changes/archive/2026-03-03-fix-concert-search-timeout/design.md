## Context

The `SearchNewConcerts` RPC calls Gemini API with Google Search grounding to discover concerts. The frontend's Connect transport has no `timeoutMs` configured, so the client doesn't declare a deadline. The server uses a global `http.TimeoutHandler` at 5s (`config.go:153`, `connect.go:123`) as insurance, but 5s is too short for Gemini + grounding (typically 2–5s, peaks higher).

The frontend already has a `createRetryInterceptor` (`connect-error-router.ts:49`) that retries `DeadlineExceeded` and `Unavailable` errors up to 3 times with exponential backoff (200ms/400ms/800ms). However, these retries hit the same 5s server wall, so they fail too.

Current flow:
```
Frontend
  createConnectTransport({baseUrl})         ← no timeoutMs
  ├── retryInterceptor (3x, 200/400/800ms)  ← retries but server kills at 5s
  └── searchNewConcerts(artistId)           ← no signal/timeout

Backend
  http.TimeoutHandler(5s)                   ← insurance, but acts as primary
  └── ConcertSearcher.Search               ← Gemini API, no retry
```

## Goals / Non-Goals

**Goals:**
- Set client-side `timeoutMs` on `searchNewConcerts` so the client controls its own deadline (20s)
- Raise the server's insurance `http.TimeoutHandler` to 30s so it doesn't pre-empt client deadlines
- Add retry with exponential backoff in the Gemini caller so transient API failures are retried server-side

**Non-Goals:**
- Making `SearchNewConcerts` fully asynchronous
- Adding per-route `http.TimeoutHandler` (the global insurance at 30s is sufficient)
- Setting `timeoutMs` on all RPCs globally (only `searchNewConcerts` needs a long timeout)

## Decisions

### Decision 1: Client-side `timeoutMs: 20000` on `searchNewConcerts`

**Approach:** Pass `{ timeoutMs: 20000 }` as the second argument to `this.concertClient.searchNewConcerts()` in `concert-service.ts:94`. This sends a `Connect-Timeout-Ms` header, letting the server know the client's deadline.

**Why 20s:** Gemini + grounding takes 2–5s per attempt. With up to 3 server-side retries (1s, 2s backoff), worst case is ~15s. 20s gives headroom.

**Why not set at transport level:** Other RPCs (List, ListByFollower) are fast (<1s). A global `timeoutMs` would be too generous for them or too tight for SearchNewConcerts.

**Callers:**
- `artist-discovery-service.ts:306` — fire-and-forget, no signal. The `timeoutMs` in `concert-service.ts` handles the deadline.
- `loading-sequence-service.ts:136` — passes a signal from a 10s global timeout. The `timeoutMs: 20000` won't conflict because the signal will abort earlier if needed.

### Decision 2: Raise `SERVER_HANDLER_TIMEOUT` from 5s to 30s

**Approach:** Change the default in `config.go:153` from `5s` to `30s`.

**Why 30s:** This is insurance, not the primary deadline. It must be higher than any client-declared `timeoutMs` (20s) to avoid pre-empting the client. 30s gives 10s of headroom.

**Why not per-route:** `http.TimeoutHandler` wraps the entire HTTP mux. Per-route wrapping would require restructuring the server setup. Since 30s is still a reasonable insurance value for all RPCs (the client's `timeoutMs` provides the tight deadline), a global increase is simpler.

**Risk:** Other RPCs without client `timeoutMs` could theoretically run for up to 30s. In practice, all other RPCs complete in <1s and are bounded by their own DB query timeouts.

### Decision 3: Retry with exponential backoff in `ConcertSearcher.Search`

**Approach:** Wrap the `client.Models.GenerateContent` call (`searcher.go:205`) in a retry loop:
- Max attempts: 3
- Backoff: 1s, 2s (exponential, base 1s, factor 2x)
- Retryable: Gemini API errors — HTTP 504 (Gateway Timeout), 503 (Unavailable), 429 (Too Many Requests), 499 (Client Cancelled on Gemini side)
- Non-retryable: `context.Canceled`, `context.DeadlineExceeded` from parent context, HTTP 400/401/403

**Key distinction:** Before each retry, check `ctx.Err()`. If the parent context (from client's `timeoutMs`) is done, stop immediately — don't waste resources.

**Where:** Inside `ConcertSearcher.Search`, wrapping only the `GenerateContent` call. Prompt construction, logging setup, and response parsing happen once.

## Risks / Trade-offs

**[Risk] Raising global `SERVER_HANDLER_TIMEOUT` to 30s weakens protection for other RPCs** → Mitigated by client-side `timeoutMs` on RPCs that need tight deadlines. Other RPCs complete in <1s and have DB-level timeouts. The 30s is purely insurance against runaway requests.

**[Risk] Frontend `retryInterceptor` + backend retry = retry amplification** → The frontend retries on `DeadlineExceeded` (3x), and the backend retries Gemini calls (3x). Worst case: 3 frontend retries × 3 backend retries = 9 Gemini calls per artist follow. This is acceptable for fire-and-forget during onboarding (~3 artists). If this becomes a concern, the frontend retry for `searchNewConcerts` can be disabled by passing a custom `interceptors` option.

**[Risk] `loading-sequence-service.ts` has a 10s global timeout but `timeoutMs` is 20s** → The AbortSignal from the 10s timeout will cancel the request before the 20s `timeoutMs` expires. This is correct — the loading sequence should be snappy, and the `timeoutMs` is just the per-RPC ceiling.
