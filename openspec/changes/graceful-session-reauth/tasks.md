## 1. Unified single-flight refresh (shared auth service)

- [x] 1.1 In `shared/services/auth-service.ts`, add one single-flight refresh method (e.g. `ensureFreshToken()` / a shared in-flight promise) that runs at most one `signinSilent()` at a time and returns the resulting user (or null)
- [x] 1.2 Route `restoreSession()` (boot) through the same single-flight promise so a boot restore and an early-RPC 401 cannot run two concurrent `signinSilent()` calls
- [x] 1.3 Remove the interceptors' own module-level `refreshPromise`; the consumer `connect-error-router` and the `admin-auth-retry-interceptor` both delegate to the service's single-flight refresh

## 2. Resume-time refresh (visibilitychange)

- [x] 2.1 Add a resume hook: on `document` `visibilitychange` → `visible`, if the stored user is authenticated AND the access token is expired or within a skew window (~60s), call the single-flight refresh before the next RPC
- [x] 2.2 Skip when the token is still valid (outside skew) and when there is no stored user (guest)
- [x] 2.3 Register for all three entries via the shared surface; idempotent listener (no duplicates); leave the consumer `resume-revalidator` (data) untouched

## 3. Reactive refresh contract + bounds

- [x] 3.1 On `Unauthenticated` for an authenticated caller: single-flight refresh → retry the original request once with the new token; return the retried result to the caller
- [x] 3.2 Bound the retry to once per request (retried request still `Unauthenticated` → do NOT loop; treat as unrecoverable)
- [x] 3.3 Guest/no-session caller: `Unauthenticated` propagates unchanged (no refresh, no forced logout) — keep the consumer's `if (!auth.user) throw`; keep admin consistent

## 4. Graceful failure (no raw text) + forced-logout parity

- [x] 4.1 On unrecoverable expiry: publish the `SignedOut` event (same cleanup as voluntary `signOut()`) so user-specific stores self-clear — fix the forced-logout path that skips it today
- [x] 4.2 Preserve return-to: capture the pre-logout location and return the user there after re-authentication (not a default landing)
- [x] 4.3 Present a neutral "session expired — signing you back in" state; never render the transport-level string
- [x] 4.4 Map `Code.Unauthenticated` to the neutral state at every route/error mapper (e.g. admin organizers route `toUserMessage` default → not `err.rawMessage`)

## 5. Tests

- [x] 5.1 Resume with expired token → exactly one `signinSilent()`; next RPC uses the fresh token
- [x] 5.2 Resume with valid token → no `signinSilent()`
- [x] 5.3 Concurrent triggers (boot restore + 401, N concurrent 401s, resume + 401) → single `signinSilent()` (single-flight)
- [x] 5.4 Reactive refresh retries the original request once; retried-still-401 → no loop, unrecoverable
- [x] 5.5 Forced logout publishes `SignedOut`; return-to preserved
- [x] 5.6 Guest 401 → propagates, no refresh/logout
- [x] 5.7 Unrecoverable expiry → neutral state, no raw `"exp" not satisfied` string rendered
- [x] 5.8 `make check` passes (frontend)

## 6. Ship to prod + verify

- [ ] 6.1 Frontend PR merged → release → shipped (consumer/admin/organizer images)
- [ ] 6.2 Cloud-provisioning prod pin bumped (if required) → ArgoCD synced
- [ ] 6.3 Verify in prod on the admin console: idle > 30 min → resume → create an Organizer with NO 401 in the console and NO error text; confirm fan-web and organizer console unaffected
