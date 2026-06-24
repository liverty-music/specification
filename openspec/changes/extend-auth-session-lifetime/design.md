## Context

Users report being signed out when reopening the installed PWA the day after sign-up, despite a 30-day refresh token. Investigation found three contributing factors:

1. **oidc-client-ts issue #2012** — `automaticSilentRenew` schedules renewal relative to a *not-yet-expired* access token. On a cold start with an *already-expired* access token, the library drops the renewal timer based on the access token alone and never consults the still-valid refresh token. The user lands unauthenticated.
2. **OIDC token lifetimes are unset in IaC** — `cloud-provisioning` configures Zitadel login-policy lifetimes (`passwordCheckLifetime`, etc.) but never the instance-level OIDC token lifetimes. Access tokens run on Zitadel's 12h built-in default; refresh tokens on 30d/90d defaults.
3. **`monitorSession` enabled in prod** — `auth-service.ts` sets `monitorSession: !import.meta.env.DEV`. The self-hosted Zitadel serves `check_session_iframe` with `frame-ancestors 'none'`, so the hidden iframe cannot load and can fire spurious `userUnloaded` events. Dev already disables it; prod does not.

Current code: `frontend/shared/services/auth-service.ts` (constructor calls `getUser()` then resolves `ready` immediately). Zitadel IaC: `cloud-provisioning/src/zitadel/` using `@pulumiverse/zitadel` `^0.2.0`, which exposes `zitadel.DefaultOidcSettings`.

## Goals / Non-Goals

**Goals:**
- A returning user with a valid refresh token is transparently re-authenticated on cold start, with no signed-out flash, regardless of how long the app was closed (within refresh-token validity).
- OIDC token lifetimes are explicit and reviewable in IaC: access 30m, refresh idle 30d, refresh absolute 90d.
- Remove the prod-only `monitorSession` iframe conflict.

**Non-Goals:**
- Real-time cross-app / IdP-side logout detection (deferred to next-refresh detection by disabling `monitorSession`).
- Refresh-token rotation policy changes beyond lifetimes.
- Any backend JWT-validation change — the backend already validates `exp`; a 30m access token simply expires sooner.
- Forking or patching `oidc-client-ts` to fix #2012 upstream.

## Decisions

### Decision 1: Boot-time silent renewal in the AuthService constructor

Gate the `ready` promise on a boot-time renewal attempt. In the constructor's `getUser()` continuation, if `user && user.expired`, call `signinSilent()` and only resolve `ready` after it settles; on success use the renewed user, on failure fall back to `null` (signed out).

```
user = await getUser()
if (user?.expired) {
  try { user = await userManager.signinSilent() }
  catch { user = null }
}
updateState(user)
readyResolve()
```

**Why over alternatives:**
- *Rely on `automaticSilentRenew` alone* — rejected: that is exactly what #2012 breaks for the cold-start-expired case.
- *Patch/fork oidc-client-ts* — rejected: maintenance burden; the public `signinSilent()` API already does the right thing when called explicitly.
- *Lazily renew on first 401 from the API* — rejected: the UI would still flash signed-out during boot, and not every landing route makes an immediate API call. Gating `ready` keeps `AuthHook` and route VMs observing a settled state.

`AuthHook.canLoad` already `await this.authService.ready`, so gating `ready` on the renewal is sufficient — no route-guard change needed.

### Decision 2: `monitorSession: false` in all environments

Replace `monitorSession: !import.meta.env.DEV` with `monitorSession: false`. Session-change detection degrades from ~2s iframe polling to next-token-refresh detection (≤30m), which is acceptable for this product and is the standard posture for SPAs against a Zitadel that blocks iframe embedding.

### Decision 3: Instance-level `DefaultOidcSettings` via Pulumi

Add a single `zitadel.DefaultOidcSettings` resource bound to the existing Zitadel provider. **All four fields are required inputs** in `@pulumiverse/zitadel` `^0.2.0` (`accessTokenLifetime`, `idTokenLifetime`, `refreshTokenExpiration`, `refreshTokenIdleExpiration`), so the resource must specify every one even though only three are behavior-relevant to this change:

| Field | Value |
|---|---|
| `accessTokenLifetime` | `30m0s` |
| `idTokenLifetime` | `12h0m0s` (keep Zitadel default — ID token is refreshed alongside access on silent renew; no need to shorten) |
| `refreshTokenExpiration` | `2160h0m0s` (90d) |
| `refreshTokenIdleExpiration` | `720h0m0s` (30d) |

This is an **instance-level** (not org-level) setting, applied once per environment stack.

## Risks / Trade-offs

- **[`signinSilent()` adds latency to cold boot]** → It only fires when the access token is expired (the long-gap reopen case), and runs concurrently with app bootstrap behind the existing `ready` barrier that routes already await. The common warm-reopen path (token still valid) skips it entirely.
- **[Disabling `monitorSession` delays IdP-side logout detection]** → Bounded by the 30m access-token lifetime; the next refresh against a revoked session fails and signs the user out. Acceptable for a consumer notification app.
- **[Longer refresh-token absolute lifetime (90d) widens the re-auth window]** → Offset by the much shorter 30m access token (was 12h), which is the actually-revocation-relevant exposure; net security posture improves.
- **[`idTokenLifetime` left at 12h while access is 30m]** → Harmless: the ID token is reissued on every silent renew; its lifetime only bounds staleness of the cached profile between renewals.
- **[Changing instance OIDC defaults affects all OIDC apps in the instance (frontend SPA, admin console)]** → Intended; all first-party apps benefit from the same posture. No app currently depends on the 12h access default.

## Migration Plan

1. **frontend** PR: boot-time silent renew + `monitorSession: false` + unit tests. No proto/BSR dependency.
2. **cloud-provisioning** PR: add `DefaultOidcSettings` resource. Apply to dev stack first (note: dev env is intentionally stopped — verify via `pulumi preview` / apply when the stack is reachable), then prod.
3. Order is independent — neither PR blocks the other; both can merge in parallel.
4. **Rollback**: frontend — revert the commit (behavior returns to immediate `ready` resolve). cloud-provisioning — `pulumi destroy` the `DefaultOidcSettings` resource reverts to Zitadel built-in defaults.

## Open Questions

- None blocking. Confirm whether prod Zitadel stack is currently reachable for `pulumi up`, or whether the OIDC-settings apply must wait for an env window (per the stopped-dev-env constraint).
