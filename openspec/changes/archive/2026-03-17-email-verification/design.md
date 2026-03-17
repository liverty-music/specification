## Design Decisions

### Zitadel Action (already implemented)

`add-email-claim.js` already injects both `email` and `email_verified` claims into access tokens via `PRE_ACCESS_TOKEN_CREATION`. Machine users (no `human` field) are skipped. No changes needed.

### Backend: Claims + JWTValidator + Interceptor

**Claims struct** — Add `EmailVerified bool` field to `auth.Claims`.

**JWTValidator** — Extract `email_verified` from JWT private claims. The claim is a boolean set by the Zitadel Action. If the claim is missing, default to `false` (fail-closed). This extraction happens alongside the existing `email` extraction in `ValidateToken()`.

**ClaimsBridgeInterceptor** — No changes needed. The interceptor already bridges `*Claims` from authn info to context. The new field is carried automatically.

**Email verification enforcement** — Add a new `EmailVerificationInterceptor` as a Connect-RPC interceptor that checks `Claims.EmailVerified`. This is separate from `ClaimsBridgeInterceptor` to maintain single responsibility:
- Runs after `ClaimsBridgeInterceptor` (claims must be in context first)
- Reads claims from context via `GetClaims()`
- If claims exist and `EmailVerified == false`, returns `connect.CodeUnauthenticated` with message "email verification required"
- If claims are nil (public endpoint, machine user), passes through — the existing auth layer already handles access control
- Skips check if `Email` is empty (machine user token without email claim)

**Why a separate interceptor instead of modifying ClaimsBridgeInterceptor**: The bridge interceptor's responsibility is context propagation, not authorization. Mixing enforcement into it would violate SRP and make it harder to disable the check for specific scenarios (e.g., machine users).

### Frontend: Auth Callback Check

In `auth-callback-route.ts`, after `handleCallback()` returns the user, check `user.profile.email_verified`. If `false` or `undefined`, set an error message and return `true` (render error) instead of proceeding to provisioning. The error message should instruct the user to check their email for a verification link.

This check happens before `provisionUser()` to prevent creating backend users with unverified emails.

## Integration Order

1. Backend changes first (Claims, JWTValidator, interceptor) — these are independent
2. Frontend change — can be done in parallel since it only reads the ID token, not the access token
3. Both PRs can be merged independently since the Zitadel Action already emits the claims
