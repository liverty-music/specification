## Why

Users experience forced logout after every PWA update. Zitadel logs confirm two occurrences of `Errors.OIDCSession.RefreshTokenInvalid (400)` at 06:31 and 07:39 on 2026-07-28, both coinciding exactly with SW deployments.

Two independent refresh token rotation races are responsible:

**Race 1 — SW reload vs automaticSilentRenew timer**

`oidc-client-ts` runs `automaticSilentRenew` (default `true`) — a background timer that fires 60 seconds before the access token expires. When a new SW is deployed:

1. The timer fires on the old page, sending a `POST /oauth/v2/token` (refresh_token grant).
2. The old page is simultaneously being unloaded by the SW reload.
3. The new page starts, `restoreSession()` finds an expired token, and calls `signinSilent()` with the **same** refresh token still in localStorage (the old page's async request hasn't updated it yet).
4. Zitadel rotates the refresh token on first use and rejects the second with `RefreshTokenInvalid`.

**Race 2 — Parallel RPC 401s in connect-error-router**

`createAuthRetryInterceptor` calls `signinSilent()` independently for each in-flight RPC that receives `Unauthenticated`. If the access token expires while multiple requests are in flight, all interceptors fire `signinSilent()` concurrently. The first use rotates the refresh token; subsequent uses receive `RefreshTokenInvalid`.

## What Changes

**Fix A**: Disable `automaticSilentRenew` in the `UserManager` settings. The background timer is removed entirely. Token refresh moves to on-demand only: `restoreSession()` at boot and `connect-error-router` on 401. This is the RFC 9700 refresh-on-demand pattern, consistent with PWA best practices when combined with refresh token rotation.

**Fix B**: Add a singleton refresh promise to `connect-error-router`. When a `signinSilent()` is already in progress, concurrent 401 interceptors await the same promise rather than issuing a new refresh request. The promise is cleared in `.finally()` so the next expiry cycle can start fresh.

## Capabilities

### Modified Capabilities

- `authentication`: Silent token refresh strategy changes from proactive timer-based (`automaticSilentRenew`) to reactive on-demand only (401 → `signinSilent`).
- `http-retry`: The auth retry interceptor gains deduplication — concurrent 401s share a single `signinSilent()` call instead of each issuing an independent refresh request.

## Impact

- `shared/services/auth-service.ts`: add `automaticSilentRenew: false` to `createSettings()`
- `src/services/connect-error-router.ts`: introduce module-level `refreshPromise` singleton
- No backend changes; no proto changes; no cloud-provisioning changes
- Admin console (`admin/`) has its own `admin-transport.ts` and is unaffected
