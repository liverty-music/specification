## Why

The Gemini-based concert search is failing silently for a significant portion of artists in production. Two distinct bugs cause data loss: (1) responses exceeding `maxOutputTokens` are truncated mid-JSON, causing 100% parse failure for affected artists (~20% of batch), and (2) Gemini returns the literal string `"null"` for unknown start times, triggering noisy WARN logs. Both were identified from dev environment logs on 2026-03-06. Ref: liverty-music/backend#151, liverty-music/backend#152.

## What Changes

- Increase `maxOutputTokens` from 8192 to 16384 to reduce the frequency of truncated responses
- Detect `FinishReason: MAX_TOKENS` before attempting JSON parse and return an explicit error instead of crashing on malformed JSON
- Update Gemini schema descriptions for `start_time` and `open_time` from "Return null if unknown" to "Return empty string if unknown" to align with `TypeString`
- Add guard for the literal string `"null"` in start_time/open_time parse logic so it is treated as unknown (nil) without a WARN log

## Capabilities

### New Capabilities

None. This is a bug fix in the existing infrastructure layer.

### Modified Capabilities

None. The `concert-search` capability requirements are unchanged; only the implementation is fixed.

## Impact

- **Code**: `internal/infrastructure/gcp/gemini/searcher.go` (main fix), `searcher_test.go` (new test cases)
- **APIs**: No API changes. No proto changes.
- **Cost**: Marginal increase in Gemini API cost for previously-truncated responses (~$0.02/batch increase, negligible)
- **Reliability**: Concert discovery success rate expected to improve from ~80% to ~95%+ per batch
