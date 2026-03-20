## Context

`AsyncSearchNewConcerts` creates a single 120s context that flows through the entire pipeline:

```
bgCtx (120s) ──▶ DB lookups ──▶ Gemini API (with retries) ──▶ DB status update
                  ~100ms          ~60-120s consumed             💥 deadline exceeded
```

Three issues compound:
1. The Gemini HTTP client is created with `nil` (no per-call timeout), so each API call can consume the entire remaining budget.
2. `errInvalidJSON` is retried up to 3 times despite structured output mode being enabled — retrying produces the same truncation.
3. `markSearchCompleted`/`markSearchFailed` use the same context, which may already be expired.

## Goals / Non-Goals

**Goals:**
- Ensure search log status updates (`markSearchCompleted`/`markSearchFailed`) always succeed regardless of Gemini API duration
- Bound each Gemini API attempt to a reasonable timeout so one slow call doesn't consume the entire budget
- Avoid futile retries when structured output mode produces invalid JSON (token limit exhaustion)

**Non-Goals:**
- Increasing `maxOutputTokens` (separate investigation — may be needed but is orthogonal)
- Changing the retry strategy for genuine Gemini server errors (503, 504) — those remain retryable
- NATS stderr logging (separate change)

## Decisions

### 1. Independent context for DB status updates

`markSearchCompleted` and `markSearchFailed` will create a new `context.Background()` with a 5-second timeout instead of propagating the caller's context.

**Why not just extend `backgroundSearchTimeout`?** Extending the timeout is a band-aid — if Gemini takes longer in the future, we hit the same problem. The DB update is a simple single-row UPDATE that should never need more than a few seconds regardless of what happened upstream.

**Why `context.Background()` instead of `context.WithoutCancel(ctx)`?** The caller's context may already be cancelled. A fresh background context guarantees the update runs.

### 2. Explicit HTTP client timeout for Gemini (60s)

Pass `&http.Client{Timeout: 60 * time.Second}` to `NewConcertSearcher` in `provider.go` instead of `nil`.

**Why 60s?** The Google Maps client already uses 10s. Gemini with Google Search Grounding involves web crawling and synthesis — 60s per attempt is generous but bounded. With 3 retry attempts and backoff, the theoretical worst case is ~60+1+60+2+60 ≈ 183s, but the 120s background context will cancel retries before that point. Each individual attempt is bounded.

**Alternative considered: per-attempt context deadline inside the retry loop.** This would work but adds complexity. The HTTP client timeout achieves the same goal more simply and is consistent with how the Maps client is configured.

### 3. Treat `errInvalidJSON` as permanent error

When `ResponseMIMEType: "application/json"` and `ResponseSchema` are configured, the Gemini API guarantees structured output. If the response is still invalid JSON, it means the output was truncated due to `maxOutputTokens` being exceeded. Retrying with the same prompt and token limit produces the same truncation.

Change: wrap `errInvalidJSON` with `backoff.Permanent()` in `parseEvents`.

**What about non-structured-output mode?** Currently all calls use structured output. If a future caller doesn't, the retry would still be pointless for the same prompt — the model's response length is deterministic for the same input.

## Risks / Trade-offs

**[Risk] 60s HTTP timeout may be too aggressive for complex artists with many tour dates** → Monitor Gemini response times after deployment. The 60s timeout can be adjusted via config if needed. Current logs show most successful calls complete in 10-30s.

**[Risk] Permanent `errInvalidJSON` means no recovery for truncated responses** → This is intentional. The search log is marked as FAILED, and the CronJob retries on the next cycle (24h TTL). If truncation is systematic for certain artists, the fix is increasing `maxOutputTokens`, not retrying.

**[Trade-off] Fresh `context.Background()` for DB updates bypasses any parent cancellation signals** → Acceptable because the update is fire-and-forget with a short 5s timeout. If the DB is down, it fails fast and logs the error.
