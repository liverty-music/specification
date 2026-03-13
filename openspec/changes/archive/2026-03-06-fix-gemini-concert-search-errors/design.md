## Context

The `ConcertSearcher.Search()` method in `internal/infrastructure/gcp/gemini/searcher.go` calls Gemini with Google Search grounding to discover concerts for an artist. Two bugs exist:

1. When Gemini's response exceeds `maxOutputTokens` (8192), `FinishReason` is `MAX_TOKENS` and the JSON is truncated. The code proceeds to `json.Unmarshal` which fails. This affects ~20% of artists per batch (those with extensive tour schedules).
2. The schema declares `start_time`/`open_time` as `TypeString` but instructs "Return null if unknown." Since `TypeString` cannot represent JSON `null`, Gemini returns the literal string `"null"`, which fails `time.Parse(RFC3339, "null")`.

The caller (`concert_uc.go:executeSearch`) marks the search as failed and the CronJob retries on the next run, so no data is permanently lost — but the retry also hits the same token limit.

## Goals / Non-Goals

**Goals:**
- Eliminate `unexpected end of JSON input` errors by detecting truncated responses before parsing
- Reduce truncation frequency by increasing token headroom
- Eliminate noisy WARN logs from `"null"` string parse failures
- Add test coverage for both scenarios

**Non-Goals:**
- Best-effort JSON repair for truncated responses (fragile, risks malformed event data)
- Streaming responses to avoid token limits (architectural change, overkill for this fix)
- Changing the Gemini model or switching to structured output mode

## Decisions

### 1. Detect MAX_TOKENS and return error (not attempt repair)

**Decision**: Check `candidate.FinishReason == genai.FinishReasonMaxTokens` after receiving the response and before calling `parseEvents()`. Return an explicit error.

**Alternatives considered**:
- **Best-effort JSON repair**: Find the last complete JSON object in the truncated response and parse partial results. Rejected because truncation can occur mid-field (e.g., mid-URL or mid-date), producing invalid event data that propagates downstream.
- **Silent skip (return nil, nil)**: Treat as "no concerts found." Rejected because it silently drops real data and the caller would mark it as `completed`, preventing retry.

**Rationale**: Returning an error causes `markSearchFailed()`, which allows the CronJob to retry. Combined with the increased token limit, retries are unlikely to hit the same issue.

### 2. Increase maxOutputTokens from 8192 to 16384

**Decision**: Double the output token limit. Based on log analysis, the largest successful response used ~2,172 candidate tokens. Truncated responses were cut at ~1,566 tokens (the limit applies to total including tool_use tokens). 16384 provides sufficient headroom.

**Alternatives considered**:
- **32768 or higher**: Unnecessary — no observed response would require this. Can be revisited if 16384 proves insufficient.
- **Keep 8192**: The error detection alone doesn't solve the problem; artists would fail on every retry.

### 3. Fix schema description + add "null" guard

**Decision**: Two-pronged fix:
1. Change schema description from "Return null if unknown" to "Return empty string if unknown"
2. Add `*ev.StartTime != "null"` guard in parse logic

Both changes are needed because Gemini's output is non-deterministic — even with the updated description, previously-cached or edge-case responses may still produce `"null"`.

## Risks / Trade-offs

- **[Risk] 16384 tokens still insufficient for some artists** → Mitigation: The MAX_TOKENS detection returns a clear error and the search is retried. If this becomes frequent, the limit can be increased further with negligible cost impact (~$0.004/call difference).
- **[Risk] Schema description change affects Gemini behavior for other fields** → Mitigation: The change is scoped to `start_time` and `open_time` only. `admin_area` already uses "Return empty string if uncertain" and works correctly.
- **[Trade-off] Error on MAX_TOKENS means zero concerts for that artist on that run** → Acceptable because the CronJob retries, and with 16384 tokens the vast majority of artists will succeed.
