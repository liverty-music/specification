## 1. Specification

- [x] 1.1 Merge this `add-admin-console` change so the spec is canonical (no proto changes required — no BSR generation/release needed).

## 2. Infrastructure — Zitadel & networking (cloud-provisioning, Pulumi)

- [x] 2.1 Add an admin-org `ApplicationOidc` (public SPA, PKCE, no secret) with redirect URIs `https://admin.{base-domain}/auth/callback` and post-logout URIs `https://admin.{base-domain}/`, dev-mode + localhost URIs only for dev; mirror the consumer `web-frontend` app settings.
- [x] 2.2 Export the admin app's client id (and confirm the admin org id from `constants.ts adminOrgIdMap`) for use in the admin runtime ConfigMap.
- [x] 2.3 Add `admin.dev.liverty-music.app` and `admin.liverty-music.app` to the gateway certmap.
- [x] 2.4 Add Cloud DNS records for the admin hostnames per environment.
- [x] 2.5 `pulumi preview` for dev; present diff for approval (no auto `pulumi up` locally).

## 3. Frontend — build separation & shared layer (frontend repo)

- [x] 3.1 Create the top-level `admin/` directory and a `shared/` location; move `AuthService` and the app-config loader into `shared/` (or re-export from it) without changing consumer behavior.
- [x] 3.2 Add `admin.html` and `admin/main.ts` bootstrap; register the second entry in `vite.config.ts` (`build.rollupOptions.input`).
- [x] 3.3 Update tsconfig / Biome / Vitest configs to include the `admin/` and `shared/` roots.
- [x] 3.4 Add an import-boundary lint rule (consumer `src/` ↔ admin `admin/` only via `shared/`) and wire it into `make lint` / CI.
- [x] 3.5 Scope the PWA service worker to the consumer entry only; ensure the admin entry ships no SW and is excluded from precache.

## 4. Frontend — admin app behavior (frontend repo)

- [x] 4.1 Implement the admin bootstrap to start OIDC sign-in scoped to the admin org id (`urn:zitadel:iam:org:id:<id>`), reusing the shared `AuthService`.
- [x] 4.2 Implement the admin auth callback route (`/auth/callback`) completing the code exchange.
- [x] 4.3 Implement an authenticated route guard so all admin routes except the callback require sign-in.
- [x] 4.4 Implement the post-login welcome placeholder shell (no business features), English-only (no `@aurelia/i18n` machinery in the admin entry).
- [x] 4.5 Add unit tests for the route guard and the org-scoped sign-in; `make check` passes.

## 5. Frontend — serving image (frontend repo)

- [x] 5.1 Add an admin `Dockerfile` + `Caddyfile` (single SPA fallback `try_files {path} /admin.html`, `/config.json` no-store) serving the admin entry's build output. Keep `npm run build` as a single build producing both entries.
- [x] 5.2 Verify locally: consumer build output is unchanged and the consumer chunk graph contains no `admin/` module (build-time assertion).
- [x] 5.3 Wire the admin image build/push into the frontend CI pipeline as a second artifact to Artifact Registry.

## 6. Infrastructure — admin workload (cloud-provisioning, k8s)

- [x] 6.1 Add the admin Deployment + Service in the existing `frontend` namespace as an `admin/` sibling to `web/` (own image, spot nodeSelector, explicit requests/limits, readiness/liveness probes); the existing `frontend` ArgoCD Application picks it up.
- [x] 6.2 Add the admin HTTPRoute binding `admin.{base-domain}` (per-overlay hostname) to the admin Service on the shared external gateway.
- [x] 6.3 Add per-env `admin-app-runtime-config` ConfigMap (admin org id + admin client id + apiBaseUrl + issuer) mounted at `/config.json`; annotate the admin Deployment for Reloader.
- [x] 6.4 Add the admin image alias to the ArgoCD image-updater config.
- [x] 6.5 `kubectl kustomize` dry-run for the dev overlay (spot nodeSelector + non-empty resources present, patches apply).

## 7. Production rollout

There is no dev environment to verify against (it is intentionally shut down for
cost and not part of this rollout), so verification happens directly in prod —
the prod OIDC app, certmap, and Cloud DNS provide the real surface to test the
Google-Workspace sign-in, welcome render, and access boundary on.

- [x] 7.1 Provision the prod admin OIDC app, prod certmap, and prod Cloud DNS; run `pulumi preview` for prod and apply from the Pulumi Cloud console after approval.
- [ ] 7.2 Release the admin image to prod via the standard frontend release path (GH Release → retag → prod AR → pin-bump → ArgoCD), independently of the consumer SPA. Wire the deferred admin-prod pieces: prod-overlay opt-in (`../../base/admin` + `admin-app-runtime-config` + `admin-app` pin), `bump-prod-pin.yml` per-component image selection, and re-enable the `frontend-admin` dispatch.
- [ ] 7.3 Verify prod at `https://admin.liverty-music.app`: Google Workspace sign-in completes and the welcome placeholder renders; a non-Workspace account cannot complete sign-in; the consumer prod surface (bundle output, hostname routing, config delivery) is unchanged.

## 8. Post-merge deployment verification

- [ ] 8.1 Monitor ArgoCD sync for the admin workload in prod; confirm pods are running with the expected config.
- [x] 8.2 Document the admin release path alongside the consumer's, noting the two are independent artifacts.
