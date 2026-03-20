## 1. Decouple DB status update context

- [x] 1.1 In `concert_uc.go`, modify `markSearchCompleted` and `markSearchFailed` to create a fresh `context.WithTimeout(context.Background(), 5*time.Second)` instead of using the caller's context
- [x] 1.2 Update existing tests in `concert_uc_test.go` to verify status update succeeds even when the parent context is cancelled

## 2. Add Gemini HTTP client timeout

- [x] 2.1 In `provider.go`, pass `&http.Client{Timeout: 60 * time.Second}` to `gemini.NewConcertSearcher` instead of `nil`

## 3. Treat invalid JSON as permanent error

- [x] 3.1 In `searcher.go` `parseEvents`, wrap `errInvalidJSON` return with `backoff.Permanent()` so truncated JSON responses are not retried
- [x] 3.2 Update `searcher_test.go` to verify that invalid JSON causes immediate failure (no retry) and that the error is permanent

## 4. Verification

- [x] 4.1 Run `make check` (lint + tests) to confirm all changes pass
