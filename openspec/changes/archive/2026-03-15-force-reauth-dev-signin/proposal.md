## Why

In dev environment, Zitadel's session cookie (`passwordCheckLifetime: 240h`) keeps users authenticated for 10 days without re-prompting for passkey. This makes it impossible to test with different users without manually clearing Zitadel domain cookies. Developers waste time debugging auth flows because the session silently reuses the previous user's credentials.

## What Changes

- **Add `prompt: 'login'` to `signIn()` in dev mode**: When running in dev environment (`import.meta.env.DEV`), pass `prompt: 'login'` to `signinRedirect()` to force Zitadel to re-authenticate via passkey on every sign-in, ignoring existing session cookies.
- **No change in prod**: Production sign-in continues to reuse sessions for smooth UX.

## Capabilities

### Modified Capabilities

- `frontend-auth-flow`: `signIn()` gains environment-aware prompt parameter. Dev forces re-authentication; prod preserves session reuse.

## Impact

- **Frontend**: `src/services/auth-service.ts` — one-line change to `signIn()`
- **No backend, proto, or infrastructure changes required**
