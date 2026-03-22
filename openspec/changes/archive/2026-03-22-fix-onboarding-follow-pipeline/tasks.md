## 1. Backend: Fix Gemini ADC Authentication

- [x] 1.1 Change `httpClient` argument in `internal/di/provider.go` from `&http.Client{Timeout: 60*time.Second}` to `nil`
- [x] 1.2 Verify `internal/di/job.go` already passes `nil` (confirmed)
- [x] 1.3 Apply `context.WithTimeout(ctx, 60*time.Second)` at the `Search()` call site in `internal/usecase/concert_uc.go`
- [x] 1.4 Run `make check` to verify tests and lint pass

## 2. Frontend: Environment-Configurable Log Level

- [x] 2.1 Update `src/main.ts` `LoggerConfiguration` to resolve level from `VITE_LOG_LEVEL` env var
- [x] 2.2 Add `VITE_LOG_LEVEL=debug` to `.env` (dev environment default)
- [x] 2.3 Add `ARG VITE_LOG_LEVEL` to `Dockerfile` for CI build-arg override
- [x] 2.4 Run `make check` to verify tests and lint pass (pre-existing issues only, no regressions from this change)

## 3. Verification

- [x] 3.1 Deploy backend to dev and verify Gemini API calls succeed (200 OK) in backend logs
- [x] 3.2 Deploy frontend to dev and verify INFO-level logs appear in browser console
- [x] 3.3 Verify full onboarding flow: follow → concert search → snack notification
