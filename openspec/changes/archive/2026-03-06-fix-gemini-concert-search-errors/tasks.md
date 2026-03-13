## 1. MAX_TOKENS Handling (#151)

- [x] 1.1 Increase `maxOutputTokens` from 8192 to 16384 in `searcher.go`
- [x] 1.2 Add `FinishReason == MAX_TOKENS` check after candidate extraction in `Search()`, return explicit error before calling `parseEvents()`
- [x] 1.3 Add test case for MAX_TOKENS finish reason in `searcher_test.go` (mock response with `finishReason: "MAX_TOKENS"` and truncated JSON body)

## 2. Literal "null" String Handling (#152)

- [x] 2.1 Update schema description for `start_time` from "Return null if unknown" to "Return empty string if unknown" in `searcher.go`
- [x] 2.2 Update schema description for `open_time` with the same change
- [x] 2.3 Add `"null"` guard to `start_time` parse logic in `parseEvents()` (treat `"null"` as unknown, no WARN log)
- [x] 2.4 Add `"null"` guard to `open_time` parse logic in `parseEvents()`
- [x] 2.5 Add test case for `start_time: "null"` string in `searcher_test.go` (expect `StartTime: nil`, no error)

## 3. Verification

- [x] 3.1 Run `make check` to verify lint and tests pass
