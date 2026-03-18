## 1. Backend — Remove Email Verification Interceptor

- [x] 1.1 Delete `internal/infrastructure/auth/email_verification.go`
- [x] 1.2 Delete `internal/infrastructure/auth/email_verification_test.go`
- [x] 1.3 Remove `EmailVerificationInterceptor{}` from interceptor chain in `internal/infrastructure/server/connect.go` (line 88) and its comment (line 72)

## 2. Frontend — Remove email_verified gate and refactor provisioning

- [x] 2.1 Remove `email_verified` check and `signOut()` call from `auth-callback-route.ts` (lines 41-46)
- [x] 2.2 Refactor callback to ensureLoaded-first flow: call `ensureLoaded()` first, catch NotFound, then call `provisionUser()` only for new users
- [x] 2.3 Update `auth-callback-route.spec.ts`: remove `email_verified: false` blocking test, update provisioning tests to match the new ensureLoaded-first flow

## 3. Cloud-Provisioning — Auto-verify email on registration

- [x] 3.1 Create `src/zitadel/scripts/auto-verify-email.js` — Zitadel Action script for `PRE_CREATION` trigger that auto-verifies the user's email
- [x] 3.2 Add `autoVerifyEmailAction` and `preCreationTrigger` to `ActionsComponent` in `src/zitadel/components/token-action.ts`, using `FLOW_TYPE_INTERNAL_AUTHENTICATION` and `TRIGGER_TYPE_PRE_CREATION` (trigger type 2)`
- [x] 3.3 Verify with `pulumi preview` that the new Action and TriggerActions resources are created correctly

## 4. Specification — Update specs

- [x] 4.1 Archive change artifacts to `openspec/specs/` (authentication, identity-management, user-auth) — run `/opsx:archive` after PRs are merged
