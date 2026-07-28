## Context

The app uses `oidc-client-ts` with Zitadel (self-hosted) for OIDC authentication. Zitadel enforces **refresh token rotation** — each use of a refresh token issues a new one and invalidates the old. The frontend PWA is served by a Vite PWA service worker that triggers `location.reload()` on SW update.

Current auth flow:
- `AuthService` creates a `UserManager` with default `automaticSilentRenew: true`
- A background timer fires 60 seconds before access token expiry, calling `signinSilent()` (refresh token grant)
- On-demand refresh also happens via `createAuthRetryInterceptor` in `grpc-transport.ts` when any RPC returns `Unauthenticated`
- `restoreSession()` at boot calls `signinSilent()` if the stored token is already expired

Two race conditions both result in `RefreshTokenInvalid (400)` from Zitadel, triggering forced logout.

## Goals / Non-Goals

**Goals:**
- Eliminate `RefreshTokenInvalid` errors caused by concurrent use of the same refresh token
- Preserve seamless session continuity for authenticated users
- Keep the existing on-demand refresh path (`connect-error-router`) as the sole refresh mechanism

**Non-Goals:**
- Change the Zitadel session policy or token lifetime configuration
- Implement offline token storage or token caching beyond what oidc-client-ts provides
- Fix the admin console (`admin/`) — it has a separate transport and is unaffected

## Decisions

### D1: Disable automaticSilentRenew

Set `automaticSilentRenew: false` in `createSettings()` in `shared/services/auth-service.ts`.

This removes the background timer entirely, eliminating Race 1. Token refresh only occurs at two well-defined, non-overlapping points:
- **Boot**: `restoreSession()` — synchronous with respect to the app lifecycle (runs once, before routes load)
- **On-demand**: `connect-error-router` — triggered by a specific 401 response

**Rationale**: The RFC 9700 OAuth 2.0 Security BCP recommends treating the refresh token as a one-shot credential per request. Proactive background renewal is at odds with strict rotation because the timer cannot coordinate with page reloads. The `connect-error-router` retry pattern already handles the 401 case gracefully, making the timer redundant.

**Trade-off**: The first RPC call after access token expiry will fail and be retried with a fresh token. This adds one round trip per expiry cycle (every AT TTL, typically 5–10 minutes). The retry is transparent to the user — `connect-error-router` retries the original request with the new token before propagating the error.

### D2: Singleton refresh promise in connect-error-router

Introduce a module-level `let refreshPromise: Promise<User | null> | null = null` in `connect-error-router.ts`. The interceptor checks this variable before calling `signinSilent()`:

```
if (refreshPromise === null) {
  refreshPromise = auth.getUserManager().signinSilent()
    .catch(() => null)
    .finally(() => { refreshPromise = null })
}
const user = await refreshPromise
```

All concurrent 401 interceptors await the **same** promise. Only one `POST /oauth/v2/token` request is sent to Zitadel per expiry cycle. The refresh token is used exactly once.

**Rationale**: Even with `automaticSilentRenew: false`, Race 2 remains possible if multiple RPCs are in-flight when the access token expires (e.g., dashboard initial load). The singleton pattern is the standard deduplication technique for this problem.

**Trade-off**: The singleton is module-scoped (not DI-scoped), meaning it is shared across all `createAuthRetryInterceptor` instances. Since the interceptor is created once per transport and all transports use the same singleton, this is the correct scope. If the refresh fails, all concurrent requests receive the same error and `connect-error-router` redirects to `/welcome` once (the first caller to complete the `.finally()` reset could race, but `window.location.href = '/welcome'` is idempotent).

### D3: No change to restoreSession

`restoreSession()` already handles boot-time token expiry correctly: it calls `signinSilent()` once, synchronously with the bootstrap sequence, before any routes load. With `automaticSilentRenew: false`, there is no background timer competing with it, so no additional changes are needed.

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| One extra RPC round trip per AT expiry cycle | Certain | Transparent retry in `connect-error-router`; no visible user impact |
| Refresh token expires (long session inactivity) | Low | Zitadel session policy controls RT lifetime; existing logout-on-failure behavior is correct |
| Admin console unaffected by Fix A | N/A | Admin has its own `admin-transport.ts`; its token management is independent |
