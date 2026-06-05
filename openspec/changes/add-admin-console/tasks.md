## 1. Specification

- [ ] 1.1 Merge this `add-admin-console` change so the spec is canonical (no proto changes required — no BSR generation/release needed).

## 2. Infrastructure — Zitadel & networking (cloud-provisioning, Pulumi)

- [ ] 2.1 Add an admin-org `ApplicationOidc` (public SPA, PKCE, no secret) with redirect URIs `https://admin.{base-domain}/auth/callback` and post-logout URIs `https://admin.{base-domain}/`, dev-mode + localhost URIs only for dev; mirror the consumer `web-frontend` app settings.
- [ ] 2.2 Export the admin app's client id (and confirm the admin org id from `constants.ts adminOrgIdMap`) for use in the admin runtime ConfigMap.
- [ ] 2.3 Add `admin.dev.liverty-music.app` and `admin.liverty-music.app` to the gateway certmap.
- [ ] 2.4 Add Cloud DNS records for the admin hostnames per environment.
- [ ] 2.5 `pulumi preview` for dev; present diff for approval (no auto `pulumi up` locally).

## 3. Frontend — build separation & shared layer (frontend repo)

- [ ] 3.1 Create the top-level `admin/` directory and a `shared/` location; move `AuthService` and the app-config loader into `shared/` (or re-export from it) without changing consumer behavior.
- [ ] 3.2 Add `admin.html` and `admin/main.ts` bootstrap; register the second entry in `vite.config.ts` (`build.rollupOptions.input`).
- [ ] 3.3 Update tsconfig / Biome / Vitest configs to include the `admin/` and `shared/` roots.
- [ ] 3.4 Add an import-boundary lint rule (consumer `src/` ↔ admin `admin/` only via `shared/`) and wire it into `make lint` / CI.
- [ ] 3.5 Scope the PWA service worker to the consumer entry only; ensure the admin entry ships no SW and is excluded from precache.

## 4. Frontend — admin app behavior (frontend repo)

- [ ] 4.1 Implement the admin bootstrap to start OIDC sign-in scoped to the admin org id (`urn:zitadel:iam:org:id:<id>`), reusing the shared `AuthService`.
- [ ] 4.2 Implement the admin auth callback route (`/auth/callback`) completing the code exchange.
- [ ] 4.3 Implement an authenticated route guard so all admin routes except the callback require sign-in.
- [ ] 4.4 Implement the post-login welcome placeholder shell (no business features).
- [ ] 4.5 Add unit tests for the route guard and the org-scoped sign-in; `make check` passes.

## 5. Frontend — serving image (frontend repo)

- [ ] 5.1 Add an admin `Dockerfile` + `Caddyfile` (single SPA fallback `try_files {path} /admin.html`, `/config.json` no-store) serving the admin entry's build output. Keep `npm run build` as a single build producing both entries.
- [ ] 5.2 Verify locally: consumer build output is unchanged and the consumer chunk graph contains no `admin/` module (build-time assertion).
- [ ] 5.3 Wire the admin image build/push into the frontend CI pipeline as a second artifact to Artifact Registry.

## 6. Infrastructure — admin workload (cloud-provisioning, k8s)

- [ ] 6.1 Add the admin Deployment + Service (own image, spot nodeSelector, explicit requests/limits, readiness/liveness probes) — decide namespace (reuse `frontend` vs new `admin`) per the design open question.
- [ ] 6.2 Add the admin HTTPRoute binding `admin.{base-domain}` (per-overlay hostname) to the admin Service on the shared external gateway.
- [ ] 6.3 Add per-env `admin-app-runtime-config` ConfigMap (admin org id + admin client id + apiBaseUrl + issuer) mounted at `/config.json`; annotate the admin Deployment for Reloader.
- [ ] 6.4 Add the admin image alias to the ArgoCD image-updater config.
- [ ] 6.5 `kubectl kustomize` dry-run for the dev overlay (spot nodeSelector + non-empty resources present, patches apply).

## 7. Dev verification

- [ ] 7.1 After dev deploys, verify Google Workspace sign-in completes and the welcome placeholder renders at `https://admin.dev.liverty-music.app`.
- [ ] 7.2 Confirm the consumer SPA is unaffected: bundle output and Lighthouse/Core Web Vitals unchanged, consumer hostname routes and config delivery unchanged.
- [ ] 7.3 Confirm a non-Workspace account cannot complete sign-in.

## 8. Production rollout

- [ ] 8.1 Provision the prod admin OIDC app, prod certmap, and prod Cloud DNS; run `pulumi preview` for prod and apply from the Pulumi Cloud console after approval.
- [ ] 8.2 Release the admin image to prod via the standard frontend release path (GH Release → retag → prod AR → pin-bump → ArgoCD), independently of the consumer SPA.
- [ ] 8.3 Verify prod: admin sign-in works at `https://admin.liverty-music.app`, welcome placeholder renders, consumer prod surface unchanged.

## 9. Post-merge deployment verification

- [ ] 9.1 Monitor ArgoCD sync for the admin workload in dev and prod; confirm pods are running with the expected config.
- [ ] 9.2 Document the admin release path alongside the consumer's, noting the two are independent artifacts.
