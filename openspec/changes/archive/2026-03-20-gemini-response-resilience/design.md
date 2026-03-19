## Context

The concert search feature calls Gemini API with Grounding (Web Search) to discover upcoming concerts for an artist. The response is expected as JSON matching our `EventsResponse` struct. In production, we observed repeated `unexpected end of JSON input` errors where Gemini returned `finish_reason: STOP` but the JSON text was truncated. The current code only guards against `FinishReasonMaxTokens` and treats all other parse failures as ERROR — triggering alerts that are not actionable.

Key file: `internal/infrastructure/gcp/gemini/searcher.go`

- `searchConcerts()` (L207–L273): API call with backoff retry, response validation, delegates to `parseEvents`
- `parseEvents()` (L276–L330): Strips markdown fences, JSON unmarshals into `EventsResponse`

## Goals / Non-Goals

**Goals:**
- Gracefully handle incomplete/invalid Gemini responses without triggering ERROR alerts
- Retry transient Gemini response issues (truncated JSON, non-STOP finish reasons) within the existing backoff loop
- Improve observability: log truncated raw response text at WARN level for post-incident analysis
- Reserve ERROR level for genuine structural issues (valid JSON that doesn't match schema)

**Non-Goals:**
- Fixing the Gemini API's truncation behavior (external dependency)
- Fixing `AppErr.LogValue()` loss through `fmt.Errorf` wrapping (tracked in pannpers/go-apperr#5)
- Changing the retry backoff configuration (intervals, max tries)
- Adding structured error response to the RPC caller (async fire-and-forget flow)

## Decisions

### 1. FinishReason whitelist (not blacklist)

**Decision**: Only allow `FinishReasonStop` and empty string (streaming in-progress) to proceed to JSON parsing. All other values → retryable error inside the backoff loop.

**Why**: There are 14+ FinishReason values and new ones are added over time. A blacklist approach would silently pass unknown new reasons. Whitelisting is safer — any new unexpected reason triggers a retry and WARN log, making it visible.

**Alternative considered**: Blacklist specific known-bad reasons (MaxTokens, Safety, Recitation, etc). Rejected because it requires maintenance as the SDK evolves.

### 2. Restructure backoff loop to include response validation

**Decision**: Move FinishReason check and `json.Valid()` check into the `backoff.Retry` callback. The callback returns a parsed `[]*entity.ScrapedConcert` (not `*genai.GenerateContentResponse`), so validation failures trigger retries.

**Why**: Truncated JSON from Gemini is transient — the same query often succeeds on retry. Keeping validation inside the retry loop handles this automatically without additional retry infrastructure.

```
backoff.Retry callback:
  1. GenerateContent() → API error → retry if retryable (existing)
  2. Response received → FinishReason not in whitelist → retry (NEW)
  3. Response received → json.Valid() fails → retry (NEW)
  4. json.Unmarshal succeeds → return parsed results
  5. json.Unmarshal fails (valid JSON, wrong structure) → permanent error (NEW)
```

**Alternative considered**: Separate retry loop around `parseEvents` only. Rejected because it would duplicate backoff configuration and the transient issue originates from the API call itself.

### 3. json.Valid() pre-check with truncated raw text logging

**Decision**: Before `json.Unmarshal`, check `json.Valid()`. On failure, log WARN with:
- Truncated raw text (first 1000 characters)
- Total raw text length
- All existing context attrs (artist, model, usage metadata)

Then return as retryable error within the backoff loop.

**Why**: `json.Unmarshal` failure on invalid JSON is indistinguishable from structural mismatch. By pre-checking validity, we can:
- Log the actual broken response for diagnosis (the key missing data today)
- Classify it correctly as transient (retryable) vs structural (permanent)
- Truncate at 1000 chars to stay within Cloud Logging's entry size limits while providing enough context

**Alternative considered**: Log full raw text. Rejected due to Cloud Logging 256KB entry limit and potential for very large Gemini responses.

### 4. Error severity reclassification

**Decision**:

| Scenario | Current | New | Rationale |
|---|---|---|---|
| Non-STOP FinishReason | ERROR (via toAppErr) | WARN (retry exhausted) | External API behavior, not actionable |
| Invalid JSON from Gemini | ERROR (Unmarshal fail) | WARN (retry exhausted) | External API behavior, not actionable |
| Valid JSON, wrong structure | ERROR | ERROR (permanent) | Likely a code bug or schema change — actionable |
| Gemini API call failure | ERROR | ERROR (unchanged) | Network/auth issues — actionable |

After all retries are exhausted for transient issues, log WARN and return `nil, nil` (empty results). The caller treats this as "no concerts found" — acceptable degradation.

## Risks / Trade-offs

**[Increased API cost from retries]** → Retries are bounded by existing `MaxTries(3)`. At worst, 2 extra API calls per search. Concert search volume is low (triggered by first-follow and daily cron), so cost impact is negligible.

**[Silent data loss on persistent Gemini issues]** → If Gemini consistently returns truncated JSON for a specific artist, we'll silently return empty results instead of erroring. Mitigation: WARN logs remain visible in Cloud Logging for monitoring. The search log status is marked as "completed" with 0 results, which is distinguishable from "never searched".

**[Retry delay increases user-perceived latency]** → Concert search is async (fire-and-forget from RPC). The user gets an immediate response; results appear later. Retry delay is invisible to the user.
