> **Cross-repo task layout**: Tasks 1–7 live in `frontend` and `cloud-provisioning`; tasks 8–10 are the user-gated rollout (merges, release tag, prod cutover, archive). This specification PR ships only the OpenSpec artifacts. The companion implementation PRs (`liverty-music/frontend#358`, `liverty-music/cloud-provisioning#275`) track sections 1–7. A checked box under sections 1–7 indicates work landed on the companion branch; section 8.x items remain `[ ]` until the corresponding merge / release event fires.

## 1. Frontend — runtime config plumbing

- [x] 1.1 Create `frontend/src/config/app-config.ts` exporting: `AppConfig` interface, `IAppConfig` DI token, `loadAppConfig()` async loader (with required-field validation), `getAppConfig()` synchronous accessor (throws if pre-bootstrap), `validateEnvironmentMatchesHost(config)` for production-host cross-check
- [x] 1.2 Write unit tests (`app-config.spec.ts`): valid config resolves; missing required field throws with field name in error; environment-vs-host mismatch throws; `getAppConfig()` throws before `loadAppConfig()` is called
- [x] 1.3 Refactor `frontend/src/main.ts` to an async `bootstrap()` function: call `loadAppConfig()`, then `validateEnvironmentMatchesHost(config)`, then `initOtel(config.apiBaseUrl)`, then construct Aurelia + register `IAppConfig` instance, then `au.start()`. Wrap with `.catch(showStaticErrorPage)`
- [x] 1.4 Add a `showStaticErrorPage(err)` helper in `main.ts` (or a sibling module) that replaces `document.body.innerHTML` with a minimal error block per the `frontend-runtime-config` spec
- [x] 1.5 Migrate `frontend/src/services/auth-service.ts`: `createSettings()` accepts `AppConfig`; `AuthService` constructor resolves `IAppConfig` and passes it to `createSettings()`. Replace all 4 `import.meta.env.VITE_*` reads. Keep `import.meta.env.DEV` reads unchanged
- [x] 1.6 Migrate `frontend/src/services/grpc-transport.ts`: export `createTransport(config: AppConfig)` factory; remove the module-level `baseUrl` const. Update all callers (Aurelia DI registration in `main.ts` should hand the resolved config to the factory)
- [x] 1.7 Migrate `frontend/src/services/otel-init.ts`: `initOtel(apiBaseUrl: string)` accepts the URL as a parameter; remove the module-level read. Update `main.ts` call site
- [x] 1.8 Migrate `frontend/src/services/proof-service.ts`: read `circuitBaseUrl` from `resolve(IAppConfig)` in the constructor; treat empty string as "circuits disabled" no-op
- [x] 1.9 Migrate `frontend/src/services/push-service.ts`: read `vapidPublicKey` from `resolve(IAppConfig)` in the constructor
- [x] 1.10 Migrate `frontend/src/routes/settings/settings-route.ts`: `vapidAvailable` computed from `resolve(IAppConfig).vapidPublicKey` length
- [x] 1.11 Migrate `frontend/src/constants/preview-artists.ts`: replace module-level `import.meta.env.VITE_PREVIEW_*` reads with `getAppConfig().previewArtistIds` / `previewArtistNames`. Keep export shape (array consts) so call sites in `welcome-route` are unchanged
- [x] 1.12 Migrate `frontend/src/main.ts` log-level resolution (`resolveLogLevel`) to read from `config.logLevel`; the `import.meta.env.DEV` fallback remains
- [x] 1.13 Verify `grep -rn 'import\.meta\.env\.VITE_' frontend/src` returns empty
- [x] 1.14 Run `make lint` and fix any biome / tsc issues introduced by the refactor

## 2. Frontend — Service Worker and Caddy

- [x] 2.1 Add `registerRoute(({url}) => url.pathname === '/config.json', new NetworkOnly())` to `frontend/src/sw.ts` (above the existing artist/follow service routes for clarity)
- [x] 2.2 Update `frontend/Caddyfile`: add a `@config path /config.json` matcher with `Cache-Control: no-cache, no-store, must-revalidate` and `Content-Type: application/json; charset=utf-8` headers
- [x] 2.3 Verify Caddyfile syntax: `docker run --rm -v $PWD/Caddyfile:/etc/caddy/Caddyfile caddy:2-alpine caddy validate --config /etc/caddy/Caddyfile`

## 3. Frontend — committed dev fallback and image cleanup

- [x] 3.1 Create `frontend/public/config.json` containing dev environment values (mirrors today's `.env`). Format: JSON object matching `AppConfig`
- [x] 3.2 Delete `frontend/.env.prod`
- [x] 3.3 Update `frontend/Dockerfile`: remove `ARG VITE_MODE=""` and the conditional `if [ -n "$VITE_MODE" ]` build invocation. Replace with a plain `RUN npm run build`
- [x] 3.4 Verify `npm start` boots and serves `http://localhost:9000/config.json` with the dev values
- [x] 3.5 Verify `npm run build` produces a `dist/` that contains `config.json` (copied from `public/`)

## 4. Frontend — defense-in-depth CI assertion

- [x] 4.1 Create `frontend/scripts/verify-build-templates.ts`: glob `dist/assets/*-route-*.js`, assert each known route chunk contains its expected template marker string (e.g., `welcome-route` → `welcome-hero`). Exit non-zero with a clear message on failure
- [x] 4.2 Define the route → marker map in the script as a const at the top, with one entry per route declared in `src/app-shell.ts`. Source markers from a stable class name or `data-` attribute that appears in each route's compiled `.html`
- [x] 4.3 Add `npm run verify:build-templates` script in `package.json`
- [x] 4.4 Add unit test that runs the script against a temp dir lacking the marker and asserts non-zero exit
- [x] 4.5 Wire the script into the existing build step (either in Dockerfile after `npm run build`, or in `push-image.yaml` as a separate workflow step that runs before the docker push)

## 5. Frontend — post-deploy smoke E2E

- [x] 5.1 Create `frontend/tests/smoke/post-deploy.spec.ts` (Playwright): load the configured URL, wait for networkidle, assert `body.innerText.trim()` non-empty, assert the welcome route's first-screen element is in the DOM
- [x] 5.2 Add `BASE_URL` env var support; default to the dev URL, override per CI invocation
- [x] 5.3 Add a `config.json` fetch assertion in the same spec: response 200, environment field matches expected
- [x] 5.4 Add `npm run test:smoke` script
- [x] 5.5 Wire the smoke into the deploy workflow: run on both `main` push (against dev URL after ArgoCD sync) and on `release` (against prod URL after prod ArgoCD sync)

## 6. cloud-provisioning — ConfigMap and Deployment patch

- [x] 6.1 Add `volumes` + `volumeMounts` for `runtime-config` to `cloud-provisioning/k8s/namespaces/frontend/base/web/deployment.yaml` (mountPath `/srv/config.json`, subPath `config.json`, sourced from ConfigMap `web-app-runtime-config`)
- [x] 6.2 Add Reloader annotation `reloader.stakater.com/auto: "true"` to the Deployment template metadata
- [x] 6.3 Create `cloud-provisioning/k8s/namespaces/frontend/overlays/dev/configmap.yaml` with the `web-app-runtime-config` ConfigMap containing `config.json` key with dev values (mirrors `frontend/public/config.json`)
- [x] 6.4 Reference the ConfigMap from `overlays/dev/kustomization.yaml` `resources:`
- [x] 6.5 Create `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/configmap.yaml` with `web-app-runtime-config` containing `config.json` with prod values (from today's `.env.prod`)
- [x] 6.6 Reference the ConfigMap from `overlays/prod/kustomization.yaml`
- [x] 6.7 Run `kubectl kustomize k8s/namespaces/frontend/overlays/dev` and verify the ConfigMap renders with dev `environment: dev` plus a Deployment with the expected mount
- [x] 6.8 Run `kubectl kustomize k8s/namespaces/frontend/overlays/prod` and verify the same for prod
- [x] 6.9 Run `make lint-k8s` to ensure kube-linter passes

## 7. Frontend CI — drop VITE_MODE branches

- [x] 7.1 Update `frontend/.github/workflows/push-image.yaml`: remove the conditional `Set Image Tags` step pair if it diverged only on env-tag, OR keep tag divergence (dev `:latest,:sha,:main`, prod `:<tag>,:<sha>`) but unify the build path
- [x] 7.2 Remove `--build-arg VITE_MODE=prod` from the release/prod build step. Both paths now invoke the build with identical inputs
- [x] 7.3 Add a workflow step (or rely on Dockerfile-internal step from task 4.5) that runs `npm run verify:build-templates` before pushing the image
- [x] 7.4 Trigger a workflow_dispatch dry run to confirm the dev and release paths still pass

## 8. Coordinated rollout

- [x] 8.1 Merge specification PR (this change) — captures the contract — _PR open: liverty-music/specification#486; merge user-gated after CI passes_
- [x] 8.2 Open cloud-provisioning PR (tasks 6.x) — review in parallel — _liverty-music/cloud-provisioning#275_
- [x] 8.3 Open frontend PR (tasks 1.x–5.x, 7.x) — review in parallel — _liverty-music/frontend#358_
- [ ] 8.4 Merge cloud-provisioning PR first → ArgoCD applies, dev pod restarts via Reloader, ConfigMap mounted but old image still ignores it. Verify dev still works as today
- [ ] 8.5 Merge frontend PR → dev CI builds new image, ArgoCD Image Updater bumps dev Deployment. Verify `https://dev.liverty-music.app/` loads and `curl https://dev.liverty-music.app/config.json` returns dev values
- [ ] 8.6 Cut frontend release `v1.0.1` (or appropriate semver) on the new merge commit on `main` HEAD. Verify release CI builds and pushes to `liverty-music-prod/frontend/web-app:v1.0.1,:<sha>`
- [ ] 8.7 Update `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml` image pin to `v1.0.1`. Open + merge the pin-bump PR
- [ ] 8.8 ArgoCD syncs prod. Verify `https://liverty-music.app/` renders the welcome route (no longer blank), and `curl https://liverty-music.app/config.json` returns prod values with `environment: prod`
- [ ] 8.9 Run post-deploy smoke E2E against the live prod URL (manual or CI-triggered)

## 9. Defense-in-depth follow-ups (track separately if not done in this PR)

- [ ] 9.1 File an issue on `@aurelia/vite-plugin` GitHub repository describing the literal `mode === 'production'` check and proposing `command === 'build'` (or `config.isProduction`) as the gate. Include a minimal repro
- [ ] 9.2 (Optional) Open a PR with the proposed fix on `@aurelia/vite-plugin`
- [ ] 9.3 Document the runtime-config contract in `frontend/docs/` (or repo README) for new contributors: how `public/config.json` differs from the K8s-mounted version, where to add a new VITE_-equivalent field, the bootstrap order
- [ ] 9.4 (Phase 2, separate change) Switch release-tag CI from rebuild to retag (dev-AR → prod-AR via `gcloud artifacts docker tags add`) for true binary-identical image promotion

## 10. Archive

- [ ] 10.1 After tasks 1–8 verified in dev + prod, mark this change complete and prepare an archive PR per the repo's openspec-sync-specs pattern (move `openspec/changes/adopt-runtime-config-for-frontend/` to `openspec/changes/archive/<date>-adopt-runtime-config-for-frontend/`).
- [ ] 10.2 Merge spec deltas into canonical `openspec/specs/`:
  - **Add** new `openspec/specs/frontend-runtime-config/spec.md` (full file from this change's `specs/frontend-runtime-config/spec.md`).
  - **Edit** `openspec/specs/prod-image-pipeline/spec.md`:
    - DELETE the requirement "Frontend prod build SHALL bake env-prod values into the SPA bundle" with all three of its scenarios (Prod build resolves API endpoints to prod hostnames; Prod build uses prod SPA OIDC client_id; Prod build uses info-level logging).
    - REPLACE the requirement "Frontend prod image build SHALL be triggered by GitHub Release tags" with the MODIFIED version from this change (drops the `.env.prod` bake-time assertion, adds the env-agnostic-build + identical-Dockerfile-inputs scenarios + post-build template-presence gate scenario).
    - ADD the new requirement "Frontend prod image SHALL be env-agnostic at the bundle level" with all four of its scenarios.
  - **Edit** `openspec/specs/frontend-hosting/spec.md`:
    - APPEND the three new ADDED requirements: "Caddy SHALL serve `/config.json` with no-cache headers"; "Frontend Deployment SHALL mount a per-environment runtime-config ConfigMap"; "Post-deploy smoke verification SHALL assert the SPA renders".
    - The existing "Caddyfile configuration" requirement remains; its scenarios are unchanged in shape (no scenario deletion).
- [ ] 10.3 Run `openspec validate` against the merged canonical specs to confirm no orphan references remain (e.g., the `.env.prod` string in any spec file).
