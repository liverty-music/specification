## Why

The background concert search (`AsyncSearchNewConcerts`) shares a single 120-second context across the entire Gemini API call chain and the subsequent DB status update. When Gemini responds slowly or returns truncated JSON (triggering retries with exponential backoff), the context deadline is exhausted before `markSearchCompleted` can update the search log. This leaves search logs stuck in PENDING status, causing users to see stale "searching…" indicators and blocking subsequent searches until the 3-minute self-healing timeout expires.

A secondary issue is that `errInvalidJSON` (truncated Gemini response) is treated as a transient/retryable error. Since `ResponseMIMEType: "application/json"` and `ResponseSchema` are already configured, a truncated response from Gemini indicates an output token limit issue — retrying the same request produces the same truncation, wasting time and contributing to the deadline exhaustion.

## What Changes

- **Decouple DB update context from Gemini context**: `markSearchCompleted` and `markSearchFailed` will use an independent short-lived context (e.g., 5s) instead of the shared background context, ensuring status updates succeed even when Gemini consumes most of the deadline.
- **Add per-call timeout to Gemini HTTP client**: Pass an `http.Client` with an explicit timeout (e.g., 60s) to `NewConcertSearcher` instead of `nil`, bounding each Gemini API attempt.
- **Treat `errInvalidJSON` as a permanent error**: Since structured output mode (`ResponseMIMEType` + `ResponseSchema`) is enabled, invalid JSON indicates a systemic issue (likely `maxOutputTokens` exhaustion). Retrying is futile — fail fast and mark the search as failed.

## Capabilities

### New Capabilities

_None — this is a bug fix within existing capabilities._

### Modified Capabilities

_None — no spec-level requirement changes. The behavior contract (search → update status) remains the same; only the implementation's timeout and retry strategy changes._

## Impact

- **Backend only**: `internal/usecase/concert_uc.go`, `internal/infrastructure/gcp/gemini/searcher.go`, `internal/di/provider.go`
- **No API changes**: No proto, RPC, or DB schema changes
- **No breaking changes**: External behavior is unchanged — searches that previously timed out will now fail faster and update status correctly
