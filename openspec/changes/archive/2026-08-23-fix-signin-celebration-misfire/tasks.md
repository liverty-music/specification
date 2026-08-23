## 1. Carry the sign-up flow signal through OIDC

- [x] 1.1 In `shared/services/auth-service.ts`, update `signUp()` to pass `state: { flow: 'signup' }` to `signinRedirect` (alongside the existing `prompt: 'create'`). Leave `signIn()` without a flow marker.
- [x] 1.2 Ensure `handleCallback()` returns / exposes the resolved OIDC `User.state` (or a typed accessor for the flow marker) so `AuthCallbackRoute` can read it. Add a small type for the state shape.

## 2. Gate the celebration on the flow signal

- [x] 2.1 In `src/routes/auth-callback/auth-callback-route.ts`, read the flow marker from the callback result and set `localStorage['liverty:postSignup:shown'] = 'pending'` only when the flow is `'signup'` (per design D2, default to `flow === 'signup' && created`). Remove the sole reliance on `created`.
- [x] 2.2 Treat a missing/absent flow marker as NOT sign-up (fail closed → no celebration), per design D3.
- [x] 2.3 Update the stale code comment that claims a backend new-account signal exists to reflect the flow-signal approach.

## 3. Tests

- [x] 3.1 Unit-test the auth-callback gating: sign-up flow → flag set; sign-in flow with empty cache → flag NOT set; missing marker → flag NOT set.
- [x] 3.2 Unit-test `signUp()`/`signIn()` pass (respectively carry / omit) the `state.flow` marker to `signinRedirect`.
- [ ] 3.3 (Optional) E2E/regression: complete a sign-in with cleared local cache and assert the dashboard shows no celebration overlay / PostSignupDialog.

## 4. Verify & ship

- [x] 4.1 `make check` (lint + typecheck + unit) passes in `frontend`.
- [x] 4.2 Manually verify in a fresh browser profile: sign-in → no celebration; sign-up → celebration + PostSignupDialog once.
- [x] 4.3 Open the frontend PR, merge after CI + review.
- [x] 4.4 Ship to production via the frontend release path (GitHub Release → prod AR retag → automated pin-bump) and confirm the fix in the dev/prod environment.
