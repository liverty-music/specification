## Why

Zitadel's Hosted Login blocks the OIDC authorization flow until the user completes the email OTP step during Self-Registration. On mobile, this requires switching to the mail app, copying the OTP, and returning to the PWA — a high-friction experience that causes abandonment. Since no current feature requires a verified email, enforcing verification at signup provides no user value while adding a significant conversion barrier.

## What Changes

- **BREAKING**: Remove backend `EmailVerificationInterceptor` — `email_verified=false` users are no longer blocked from RPC calls
- **BREAKING**: Remove frontend `email_verified` check in `/auth/callback` — unverified users proceed normally through provisioning and dashboard redirect
- Configure Zitadel Login Policy to disable mandatory email verification during Self-Registration, allowing the OIDC flow to complete immediately
- Optimize frontend auth callback: call `provisionUser` only when `ensureLoaded` returns NotFound (instead of on every callback)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `authentication`: Remove "Backend Email Verification Enforcement" and "Frontend Email Verification Check" requirements. Keep "Email Verified Claim Injection" (Zitadel Action still injects the claim for future use).
- `identity-management`: Add requirement to disable email verification enforcement during Self-Registration in Login Policy.
- `user-auth`: Update registration callback scenario — remove email verification gate, add ensureLoaded-first provisioning flow.

## Impact

- **backend**: Delete `EmailVerificationInterceptor` and its test. Remove from interceptor chain in `connect.go`.
- **frontend**: Modify `auth-callback-route.ts` (remove email_verified check, refactor provisioning flow). Update `auth-callback-route.spec.ts`.
- **cloud-provisioning**: Modify Zitadel Login Policy Pulumi component to disable email verification on registration.
- **specification**: Update `authentication`, `identity-management`, and `user-auth` specs.
