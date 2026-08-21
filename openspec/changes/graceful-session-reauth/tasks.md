## 1. Resume-time silent refresh (shared auth service)

- [ ] 1.1 In `shared/services/auth-service.ts`, expose a shared single-flight refresh (one in-flight `signinSilent()` promise) reused by boot, resume, and the on-`Unauthenticated` interceptors (dedup across all three)
- [ ] 1.2 Add a resume hook: on `document` `visibilitychange` → `visible`, if the stored user is authenticated AND the access token is expired or within a skew window (~60s), trigger the shared refresh before the next RPC
- [ ] 1.3 Skip the resume refresh when the access token is still valid (outside the skew window) and when there is no stored user (guest)
- [ ] 1.4 Register the resume hook for all three entries (consumer, admin, organizer) via the shared surface; ensure it is removed/no-ops cleanly (no duplicate listeners)

## 2. Graceful `Unauthenticated` UX (no raw error)

- [ ] 2.1 Ensure a recovered `Unauthenticated` (refresh+retry success) surfaces no error to the user (verify both consumer `connect-error-router` and `admin-auth-retry-interceptor` paths)
- [ ] 2.2 On unrecoverable expiry (refresh fails), present a neutral "session expired — signing you back in" state and route to re-auth; do NOT render the transport-level string
- [ ] 2.3 Update route/error mappers (e.g. the admin organizers route `toUserMessage`) so `Code.Unauthenticated` never maps to `err.rawMessage`

## 3. Tests

- [ ] 3.1 Resume with expired access token → exactly one `signinSilent()`; subsequent RPC uses the fresh token
- [ ] 3.2 Resume with valid access token → no `signinSilent()`
- [ ] 3.3 Concurrent triggers (resume + reactive) → single-flight: only one `signinSilent()`
- [ ] 3.4 Unrecoverable expiry → neutral state, no raw `"exp" not satisfied` string rendered
- [ ] 3.5 `make check` passes (frontend)

## 4. Ship to prod + verify

- [ ] 4.1 Frontend PR merged → release → shipped (consumer/admin/organizer images)
- [ ] 4.2 Cloud-provisioning prod pin bumped (if a release bump is required) → ArgoCD synced
- [ ] 4.3 Verify in prod on the admin console: idle > 30 min → resume → create an Organizer with NO 401 in the console and NO error text; confirm the same on fan-web (still fine) and organizer console
