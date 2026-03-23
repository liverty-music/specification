## 1. Backend: Retry Strategy

- [x] 1.1 Update `isRetryable` in `internal/infrastructure/gcp/gemini/errors.go` to add 408, 500, 502, 504 as retryable status codes
- [x] 1.2 Update `isRetryable` doc comment to reflect the new retry policy and reference Google's retry strategy documentation
- [x] 1.3 Update backoff `MaxInterval` from 10s to 60s in `internal/infrastructure/gcp/gemini/searcher.go`

## 2. Backend: Context Isolation

- [x] 2.1 Modify `Search` method in `searcher.go` to create independent context per Gemini API call using `context.WithoutCancel(parentCtx)` + `context.WithTimeout(..., 120s)`
- [x] 2.2 Extract Gemini timeout duration as a named constant (e.g., `geminiCallTimeout = 120 * time.Second`)
- [x] 2.3 Update `backoff.Retry` to use the parent context for loop control while each attempt uses its own context

## 3. Backend: ConcertService Handler Timeout Isolation

- [x] 3.1 Add ConcertService-specific timeout config (or constant) for 120s handler timeout
- [x] 3.2 Modify `NewConnectServer` in `internal/infrastructure/server/connect.go` to apply 120s `http.TimeoutHandler` only to ConcertService path, keeping default 60s for other services
- [x] 3.3 Update `connect.go` function signature/DI wiring if ConcertService handler needs to be passed separately

## 4. Cloud Provisioning: Timeout Chain

- [x] 4.1 Update `GCPBackendPolicy` `timeoutSec` from 60 to 150 in `k8s/namespaces/backend/base/server/backend-policy.yaml`
- [x] 4.2 Update `configmap.env` comment for `SERVER_HANDLER_TIMEOUT` to reflect actual Gemini response times (25-110s, not 16-25s)

## 5. Tests

- [x] 5.1 Update `isRetryable` unit tests to cover new retryable status codes (408, 500, 502, 504)
- [x] 5.2 Add test for context isolation: verify `context.WithoutCancel` preserves trace but not deadline
- [x] 5.3 Verify existing `searcher_test.go` passes with updated backoff and context changes
