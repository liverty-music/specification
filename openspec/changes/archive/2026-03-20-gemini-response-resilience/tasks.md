## 1. Restructure backoff loop to return parsed results

- [x] 1.1 Change `backoff.Retry` callback return type from `*genai.GenerateContentResponse` to `[]*entity.ScrapedConcert` — move response validation and parsing logic inside the callback
- [x] 1.2 Add FinishReason whitelist check inside callback: only `FinishReasonStop` and `""` proceed; all others return retryable error with WARN log
- [x] 1.3 Remove the standalone `FinishReasonMaxTokens` check (L265–L271) — now covered by the whitelist

## 2. Add json.Valid() pre-check in parseEvents

- [x] 2.1 Add `json.Valid([]byte(text))` check before `json.Unmarshal` in `parseEvents`
- [x] 2.2 On invalid JSON: log WARN with truncated raw text (first 1000 chars), total `len(rawText)`, and context attrs; return retryable error
- [x] 2.3 On `json.Unmarshal` failure (valid JSON, wrong structure): return `backoff.Permanent` error at ERROR level

## 3. Error severity reclassification

- [x] 3.1 Ensure exhausted retries for transient issues (non-STOP finish reason, invalid JSON) result in WARN log + `return nil, nil` (not ERROR)
- [x] 3.2 Ensure structural mismatch (`json.Unmarshal` failure on valid JSON) remains ERROR via `backoff.Permanent`

## 4. Tests

- [x] 4.1 Add unit test: non-STOP FinishReason triggers retry and returns nil on exhaustion
- [x] 4.2 Add unit test: invalid JSON triggers retry and logs WARN with truncated raw text on exhaustion
- [x] 4.3 Add unit test: valid JSON with wrong structure returns permanent ERROR (no retry)
- [x] 4.4 Add unit test: transient failure on first attempt, success on retry returns parsed results
