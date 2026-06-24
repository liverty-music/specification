## Why

Users who sign up and install the PWA are signed out when they reopen the app the next day, even though their refresh token is still valid for 30 days. The root cause is a known `oidc-client-ts` bug ([#2012](https://github.com/authts/oidc-client-ts/issues/2012)): when the app cold-starts with an already-expired access token, the library drops the silent-renew timer based on the access token alone and never consults the still-valid refresh token, so the user lands unauthenticated. Compounding this, the OIDC token lifetimes are not configured in IaC at all — they run on Zitadel built-in defaults (access 12h) — and `monitorSession` is enabled in prod where Zitadel's `check_session_iframe` returns `frame-ancestors 'none'`, which can fire spurious `userUnloaded` events. For a never-miss-a-live notification app, staying signed in across long gaps is core to the value proposition.

## What Changes

- **Frontend session restoration on cold start**: On app boot, if a stored user exists but its access token is expired, the auth service SHALL attempt `signinSilent()` (refresh-token grant) and only resolve auth readiness after that attempt completes — so a valid refresh token transparently restores the session instead of presenting a signed-out UI.
- **Disable `monitorSession` in all environments**: Remove the env-conditional and set `monitorSession: false` everywhere, eliminating the Zitadel `frame-ancestors 'none'` iframe conflict that can spuriously unload the user. Cross-app/session-level logout detection is deferred to the next token refresh.
- **Explicit OIDC token lifetimes via IaC**: Configure Zitadel instance-level OIDC token lifetimes in Pulumi (previously unset = built-in defaults): `access_token_lifetime = 30m`, `refresh_token_idle_expiration = 30d`, `refresh_token_expiration = 90d`. Shorter access tokens improve security; the long refresh window keeps fans signed in across gaps, and the explicit values make the intent durable rather than dependent on Zitadel defaults.

## Capabilities

### New Capabilities
<!-- None — both behaviors extend existing capabilities. -->

### Modified Capabilities
- `user-auth`: Add a requirement for transparent session restoration on app cold-start via silent refresh-token renewal, and specify that server-side session monitoring (`monitorSession`) is disabled in all environments.
- `identity-management`: Add a requirement that OIDC token lifetimes are managed explicitly via IaC (access 30m, refresh idle 30d, refresh absolute 90d) rather than relying on Zitadel built-in defaults.

## Impact

- **frontend**: `shared/services/auth-service.ts` — boot-time silent-renew logic in the `AuthService` constructor (gating the `ready` promise) and the `monitorSession` setting. Associated unit tests (`test/auth-service.spec.ts`).
- **cloud-provisioning**: Zitadel Pulumi components — add a `DefaultOidcSettings` (instance-level OIDC token-lifetime) resource.
- **No proto / BSR changes**: This change does not touch the schema; no code generation or release of the `specification` package is required.
- **Security posture**: Access-token exposure window shrinks from 12h to 30m; refresh-token absolute lifetime is bounded at 90d (same as Zitadel default; now set explicitly) with a 30d idle window.
