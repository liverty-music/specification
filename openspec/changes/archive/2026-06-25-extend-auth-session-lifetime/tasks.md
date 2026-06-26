## 1. Frontend — Session Restoration on Cold Start

- [x] 1.1 In `shared/services/auth-service.ts`, change the constructor's `getUser()` continuation: when the loaded user exists and `user.expired` is true, await `userManager.signinSilent()` and use its result; on rejection, fall back to `null`. Resolve the `ready` promise only after this attempt settles.
- [x] 1.2 Set `monitorSession: false` unconditionally in `createSettings()` (remove the `!import.meta.env.DEV` conditional) and update the explanatory comment to reflect the all-environment rationale (Zitadel `check_session_iframe` `frame-ancestors 'none'`).
- [x] 1.3 Add/extend unit tests in `test/auth-service.spec.ts`: (a) expired access token + valid refresh → `signinSilent` invoked, ends authenticated, `ready` resolves after renewal; (b) expired access token + failed `signinSilent` → ends unauthenticated; (c) valid access token → no `signinSilent` call.
- [x] 1.4 Run `make check` in `frontend` and confirm lint + tests pass.

## 2. Cloud-Provisioning — OIDC Token Lifetimes

- [x] 2.1 Add a `zitadel.DefaultOidcSettings` resource (instance-level) in the Zitadel Pulumi stack, bound to the existing provider, with `accessTokenLifetime: '0h30m0s'`, `idTokenLifetime: '12h0m0s'`, `refreshTokenExpiration: '2160h0m0s'` (90d), `refreshTokenIdleExpiration: '720h0m0s'` (30d). All four fields are required inputs.
- [x] 2.2 Run `pulumi preview` for the prod stack and confirm the only diff is the new `DefaultOidcSettings` resource (no unintended drift). Verified: `+1 create` = `liverty-music-oidc-settings`; the `~1 update` on `dashboard-zitadel-observability` is pre-existing drift unrelated to this change.
- [x] 2.3 Run lint / typecheck for the cloud-provisioning package and confirm it passes.

## 3. Ship to Production

- [x] 3.1 Open the `frontend` PR (commit per Liverty convention with `Refs: #<issue>`); drive CI green and merge. (PR #466 — merged 2026-06-25, all checks green incl. review bot.)
- [x] 3.2 Open the `cloud-provisioning` PR; drive CI green and merge (ArgoCD / Pulumi applies the `DefaultOidcSettings` to prod). (PR #371 — merged 2026-06-25; prod `pulumi up` is a manual console step, see 3.4.)
- [x] 3.3 Cut the `frontend` GitHub Release (SemVer tag) to retag the prod image and trigger the automated prod-pin bump. (Released v1.18.0 — minor bump because the range also carried #465 `feat(analytics)`; ships #466 auth fix + #465 to prod.)
- [x] 3.4 Verify `DefaultOidcSettings` applied to the prod Zitadel instance: `GET /admin/v1/settings/oidc` (or `pulumi stack` output) reflects access 30m / idle 30d / absolute 90d. Confirmed via `pulumi stack export --stack prod`: 307 resources (+1), accessTokenLifetime=0h30m0s, idTokenLifetime=12h0m0s, refreshTokenExpiration=2160h0m0s, refreshTokenIdleExpiration=720h0m0s.

## 4. Production Verification

- [x] 4.1 On the prod PWA: sign up, install, then reopen after the access token (30m) has expired — confirm the session is silently restored and no signed-out state is shown. Verified 2026-06-25: existing installed PWA, 30+ min elapsed, session restored transparently.
- [x] 4.2 Confirm browser console shows no recurring `userUnloaded` / `frame-ancestors` errors after the `monitorSession` change. Verified 2026-06-25: no errors observed.
