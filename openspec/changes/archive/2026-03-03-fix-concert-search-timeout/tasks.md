## 1. Client-Side Timeout

- [x] 1.1 Add `timeoutMs: 20000` to `searchNewConcerts` RPC call in `frontend/src/services/concert-service.ts`

## 2. Server-Side Insurance Timeout

- [x] 2.1 Change `SERVER_HANDLER_TIMEOUT` default from `5s` to `30s` in `backend/pkg/config/config.go`

## 3. Gemini Retry Logic

- [x] 3.1 Add `isRetryable` helper to classify transient Gemini errors (504, 503, 429) vs non-retryable in `backend/internal/infrastructure/gcp/gemini/errors.go`
- [x] 3.2 Add retry loop with exponential backoff (max 3 attempts, 1s/2s delays) around `GenerateContent` call in `backend/internal/infrastructure/gcp/gemini/searcher.go`
- [x] 3.3 Check `ctx.Err()` before each retry to bail out if parent context is cancelled

## 4. Testing

- [x] 4.1 Add unit tests for `isRetryable` error classification
- [x] 4.2 Add unit tests for retry behavior (success on retry, all retries exhausted, non-retryable stops, context cancellation stops)
- [x] 4.3 Run frontend tests (`npm test`) and backend tests (`golangci-lint`, `go test ./...`)
