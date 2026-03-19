## Why

The Gemini API (with Grounding/Web Search) intermittently returns truncated JSON responses while reporting `finish_reason: STOP`. This triggers ERROR-level alerts that are not actionable — the root cause is external API instability, not a bug in our code. Additionally, the current error path loses diagnostic context (raw response text) due to `fmt.Errorf` wrapping, making root cause analysis difficult when issues do occur.

## What Changes

- Add a FinishReason whitelist check: only `STOP` (and unspecified for streaming) proceeds to JSON parsing; all other reasons are logged as WARN and treated as empty results.
- Add `json.Valid()` pre-check before `json.Unmarshal`: invalid JSON is logged as WARN with truncated raw text and response length, then treated as empty results.
- Move JSON parse failure retry into the existing `backoff.Retry` loop around `GenerateContent`, so transient Gemini response issues trigger automatic retries.
- Downgrade external-API-caused failures from ERROR to WARN, reserving ERROR for structural mismatches (valid JSON that doesn't match our schema — indicating a code bug).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `auto-concert-discovery`: Add resilience requirements for handling incomplete or invalid Gemini API responses during concert search.

## Impact

- **Backend**: `internal/infrastructure/gcp/gemini/searcher.go` — primary changes to `searchConcerts` and `parseEvents` methods.
- **Alerting**: Reduces false-positive ERROR alerts from the "Server ERROR Log" policy. Only genuine structural mismatches will trigger ERROR alerts going forward.
- **Observability**: Improved WARN-level logging with raw response text (truncated) and response length for post-incident analysis.
