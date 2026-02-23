## Why

During signup, if `UserService.Create` panics in the backend, the error is silently swallowed by the frontend and the auth flow continues. This leaves the user in a broken state where no backend record exists, causing all subsequent RPCs to fail. Additionally, the Connect interceptor chain is ordered incorrectly, causing panic logs to lack trace context and access logs to be missing entirely during panics — making the issue extremely difficult to diagnose. (GitHub Issue: liverty-music/specification#88)

## What Changes

- **Fix interceptor chain ordering**: Reorder Connect interceptors so that (1) tracing is outermost (all logs get `trace_id`), (2) access log sees converted `*connect.Error` for correct status codes, (3) recover handler sits inside tracing for traceable panic logs, and (4) access log is not bypassed during panics.
- **Add nil guard in `userUseCase.Create`**: Defensive check against `(nil, nil)` return from `UserRepository.Create` interface to prevent nil pointer dereference on `user.ID`.
- **Fix frontend error swallowing**: `provisionUser()` in `auth-callback.ts` currently catches and ignores all non-`AlreadyExists` errors. Non-retryable errors must halt the auth flow and surface an error to the user.

## Capabilities

### New Capabilities

- `interceptor-chain-ordering`: Documents the correct ordering of Connect interceptors with rationale for each layer's position in the chain.

### Modified Capabilities

- `authentication`: Backend interceptor chain ordering changes. The `ClaimsBridgeInterceptor` position relative to other interceptors is affected.
- `frontend-onboarding-flow`: Frontend auth callback error handling changes from silent swallow to explicit error surfacing.

## Impact

- **Backend (`backend/`)**: `internal/infrastructure/server/connect.go` (interceptor registration order), `internal/usecase/user_uc.go` (nil guard)
- **Frontend (`frontend/`)**: `src/routes/auth-callback.ts` (error handling in `provisionUser`)
- **Observability**: Panic and error logs will now include `trace_id`/`span_id`; access logs will show correct gRPC status codes instead of `"unknown"`
