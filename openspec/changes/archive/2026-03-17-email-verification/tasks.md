## Tasks

### Backend

- [x] Add `EmailVerified bool` field to `Claims` struct in `internal/infrastructure/auth/context.go`
- [x] Extract `email_verified` claim in `JWTValidator.ValidateToken()` — default to `false` if missing
- [x] Add `EmailVerificationInterceptor` in `internal/infrastructure/auth/email_verification.go` — check `Claims.EmailVerified`, return `connect.CodeUnauthenticated` if false, skip if no email claim (machine user)
- [x] Wire `EmailVerificationInterceptor` into the Connect-RPC handler chain (after `ClaimsBridgeInterceptor`)
- [x] Update tests: `context_test.go`, `jwt_validator_test.go`, new `email_verification_test.go`, update `authn_test.go` if needed

### Frontend

- [x] In `auth-callback-route.ts`, check `user.profile.email_verified` after `handleCallback()` — if not verified, display error and block provisioning
