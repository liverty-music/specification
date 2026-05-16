## Why

The current frontend bakes per-environment values (`VITE_API_BASE_URL`, `VITE_ZITADEL_*`, `VITE_VAPID_PUBLIC_KEY`, etc.) into the Vite-built SPA bundle via `.env.prod` loaded by `vite build --mode prod`. This approach is structurally fragile and **already produced a Sev-1 regression**: the v1.0.0 prod release renders a blank page at `https://liverty-music.app/` because `@aurelia/vite-plugin@2.0.0-rc.1` literal-checks `mode === 'production'` when bundling component templates ([node_modules/@aurelia/vite-plugin/src/index.ts:64](frontend/node_modules/@aurelia/vite-plugin/src/index.ts#L64)) — any non-`'production'` mode name silently strips templates from lazy route chunks, leaving Aurelia unable to resolve any route (`AUR3174 Failed to resolve VR(component:'unnamed-20')`).

This vulnerability exists in every per-env build that uses a non-`production` mode name. The same class of bug will recur for any future build-time flag that interacts with Vite's `mode`. We have a **single non-recurring window** to fix it cleanly: prod is tagged `v1.0.0` but has zero users (blank page, no PWA installs, no auth sessions, no cached service workers). After service-in, migrating away from build-time env baking becomes 10× more expensive because of installed PWAs, cached SWs, and live user sessions that would need coordinated invalidation.

## What Changes

- **BREAKING (internal-only, pre-service-in)**: Replace build-time `.env.prod` bake with **runtime config injection** via `/config.json` served by Caddy from a K8s ConfigMap mounted per environment.
- Single container image promoted across environments (dev/prod) — image binary is env-agnostic. Per-env divergence moves to ConfigMap content under `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/`.
- New `AppConfig` DI token + async bootstrap that fetches and validates `/config.json` before `Aurelia.start()`. All 8 `import.meta.env.VITE_*` read sites migrate to `resolve(IAppConfig)`.
- `import.meta.env.DEV` / `PROD` / `MODE` reads (5 sites) are NOT migrated — they retain their original semantics ("`vite` dev server vs `vite build` output") and are env-agnostic.
- Remove `.env.prod` from the frontend repo and `VITE_MODE` build-arg from the Dockerfile. Vite mode stays `'production'` always — Aurelia plugin's template bundling path stays deterministic.
- Add post-build assertion in CI: every route chunk MUST contain HTML-template-derived strings (defense against a future analogous regression).
- Add post-deploy smoke E2E (Playwright) that hits the live URL and asserts non-empty DOM + correct `environment` field in `/config.json`.
- File upstream issue / PR on `@aurelia/vite-plugin` to use `config.command === 'build'` instead of literal mode check.

## Capabilities

### New Capabilities
- `frontend-runtime-config`: Defines the runtime configuration contract for the frontend SPA — the `/config.json` schema, the bootstrap load order, the validation/cross-check guards (environment field vs. window hostname), Service-Worker pass-through rules for the config endpoint, and the contract between the SPA bundle and the per-environment K8s ConfigMap.

### Modified Capabilities
- `prod-image-pipeline`: The "Frontend prod build SHALL bake env-prod values into the SPA bundle" requirement is REMOVED. Replaced by an invariant that the frontend image SHALL be env-agnostic at the bundle level. The release-triggered prod-AR push requirement is preserved but its `.env.prod` bake-time assertion is replaced with a "no env-divergent strings in bundle" assertion.
- `frontend-hosting`: Adds requirements for Caddy to serve `/config.json` with no-cache headers, for the Deployment to mount a per-env ConfigMap volume at `/srv/config.json` (with Reloader annotation for rollout-on-change), and for the Service Worker to bypass the precache for `/config.json`.

## Impact

**Affected repos**:
- `frontend` (largest surface): `src/main.ts` (async bootstrap), new `src/config/app-config.ts`, 8 service/route/constant files migrated to DI, `src/sw.ts` (NetworkOnly route for `/config.json`), `Caddyfile` (cache headers), `Dockerfile` (drop `VITE_MODE`), `public/config.json` (dev fallback), delete `.env.prod`.
- `cloud-provisioning`: New `ConfigMap` per overlay (`overlays/dev/`, `overlays/prod/`), Deployment volumeMount patch in `namespaces/frontend/base/web/deployment.yaml`, Reloader annotation. No Pulumi changes (ConfigMap content lives in Kustomize, same as other static config).
- `specification`: This change.

**Affected CI**:
- `frontend/.github/workflows/push-image.yaml`: Drop `VITE_MODE` build-arg from prod path. Both push and release paths build with identical inputs. Optional follow-up: switch to dev-AR → prod-AR retag (true build-once-promote); deferred to Phase 2.
- New job: post-build template-presence assertion (defense-in-depth).
- New job: post-deploy smoke E2E.

**Affected dependencies**:
- `@aurelia/vite-plugin@2.0.0-rc.1`: unchanged; upstream issue/PR filed as parallel deliverable.
- `oidc-client-ts`, `@connectrpc/connect-web`, OTel SDK: API_BASE_URL / ZITADEL_ISSUER / etc. now sourced from `AppConfig` at construction time rather than at module-eval time.

**User-facing impact**:
- Pre-service-in (v1.0.0 prod is blank, no real users). Zero session/cookie/SW invalidation cost.
- After this change: blank-page regression fixed; prod renders normally.
- Bootstrap adds ~5ms (intra-pod fetch to Caddy) — imperceptible.

**CSP**:
- No changes. Existing `connect-src 'self' https://*.zitadel.cloud https://*.liverty-music.app` already covers both dev and prod hosts via wildcard. Tightening CSP per-env is a future concern, decoupled from this change.

**Security posture**:
- All `VITE_*` values are already classified as public by SPA convention (per the archived `prepare-prod-service-in` design D3). No new secret surface introduced. ConfigMap content is committed to Git under `cloud-provisioning`, same trust boundary as today's `.env`.

**Coordination with `prepare-prod-service-in`**:
- `prepare-prod-service-in` is in-flight in a worktree; this change SUPERSEDES the build-time portions of its D2 (`.env.prod` overlay) and D3 (env values committed to repo) while preserving its prod AR / Workload Identity / image-pin portions. The two changes will reconcile at merge time — this change is authored against `main` and is independent of `prepare-prod-service-in`'s merge order.
