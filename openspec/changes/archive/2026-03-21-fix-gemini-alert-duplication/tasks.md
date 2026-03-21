## 1. Demote infrastructure-layer log level

- [x] 1.1 Change `s.logger.Error` to `s.logger.Warn` at `internal/infrastructure/gcp/gemini/searcher.go:227`

## 2. Add HTTP 401 to retry list

- [x] 2.1 Add `http.StatusUnauthorized` to the `isRetryable` switch in `internal/infrastructure/gcp/gemini/errors.go`
- [x] 2.2 Add test case for 401 in `isRetryable` unit tests

## 3. Verify

- [x] 3.1 Run `make check` to confirm lint and tests pass
