## Context

The frontend (Aurelia 2 SPA, Vite-built, Caddy-served, ArgoCD-deployed) currently uses build-time environment substitution: `vite build --mode prod` loads `.env` + `.env.prod`, Vite embeds `import.meta.env.VITE_*` values into the bundle, and the prod container image is built distinctly from the dev container image. This was introduced by the in-flight `prepare-prod-service-in` change (commit c4fae04, 2026-05-15).

Two structural problems surfaced:

1. **Aurelia plugin's mode coupling**: [`@aurelia/vite-plugin@2.0.0-rc.1`](../../../../frontend/node_modules/@aurelia/vite-plugin/src/index.ts) gates template-bundle code generation on a literal `config.mode === 'production'` check. The mode name `'prod'` (chosen to match `.env.prod` filename) is not `'production'`, so the plugin skips rewriting `.html` imports to `.$au.ts` virtual modules. Templates fall out of every lazy route chunk. Aurelia at runtime registers the route classes without CustomElement metadata under synthetic names (`unnamed-N`), and the router cannot resolve any route → blank screen across the entire app.

2. **Per-env image divergence**: even without the bug, baking env values into the image means the artifact tested in dev is not the artifact deployed to prod. Future regressions can hide in the env-specific build path (as this one did — the c4fae04 spot-check verified env *values* were embedded but not that *templates* were).

Empirically confirmed (binary diff of live chunks):
- Dev `welcome-route-CJhWb1QO.js`: 9115 bytes, contains template strings (`welcome-hero`, `Hero`, `Live`).
- Prod `welcome-route-CHv2U1al.js`: 6158 bytes, template strings absent.

Current state pre-decision:
- `https://liverty-music.app/` is live but blank (HTTP 200, Caddy serving valid `index.html`, JS chunks 200, but Aurelia bootstrap fails).
- v1.0.0 frontend GitHub Release tagged, `liverty-music-prod/frontend/web-app:51f5bce…` in prod AR, ArgoCD synced to prod cluster.
- Zero real users (PWA installs, auth sessions, SW caches) on prod — this change can land with **no user-facing migration cost**.

Frontend code inventory grounding the design:
- 8 `import.meta.env.VITE_*` read sites: `services/auth-service.ts` (4 reads), `services/grpc-transport.ts` (1, module const), `services/otel-init.ts` (1), `services/push-service.ts` (1, class field), `routes/settings/settings-route.ts` (1, class field), `services/proof-service.ts` (1, module const), `constants/preview-artists.ts` (2, module consts), `src/main.ts` (1, LOG_LEVEL).
- 7 `import.meta.env.DEV` reads (`main.ts`, `auth-service.ts`, `preview-artists.ts`) — these encode "running under `vite` dev server vs. running from a `vite build` artifact". This semantic is orthogonal to which K8s environment serves the bundle and SHALL be preserved.
- Existing CSP (`<meta http-equiv="Content-Security-Policy">` in `index.html`) already covers both envs via `connect-src 'self' https://*.zitadel.cloud https://*.liverty-music.app` wildcard.
- Existing Caddyfile is minimal: `root * /srv`, `file_server`, SPA fallback. Service Worker registered post-bootstrap via `vite-plugin-pwa` (Workbox).

Constraints:
- ArgoCD continuous-delivery model is established. Per-env Kustomize overlays under `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/` are the canonical place for env-divergent config. Reloader namespace is provisioned and used by other workloads.
- Per `prod-image-pipeline` spec: prod must pull from `liverty-music-prod/frontend/*` AR (cross-project pulls forbidden) and must NOT use `:latest` tag (explicit release tag or SHA).
- All `VITE_*` values are classified public (per `prepare-prod-service-in` D3); no secret-handling concerns here.

## Goals / Non-Goals

**Goals:**
- Eliminate the entire class of "build-mode-dependent bundle correctness" bugs by removing build-time env divergence.
- Restore correct rendering at `https://liverty-music.app/` with a single fix that does not depend on workarounds (e.g., choosing a "magic" mode name that happens to contain "production").
- Produce a single deterministic SPA bundle whose behavior is identical across environments and whose env-specific behavior is derived from `/config.json` at boot.
- Establish a defense-in-depth assertion that prevents regressions of this class (template-stripping or any analogous "bundle compiled, missing critical data" pattern).
- Keep developer ergonomics for `npm start` (Vite dev server) identical to today.
- Make adding a new environment (e.g., `staging`) a one-file Kustomize change.

**Non-Goals:**
- True bit-identical image promotion (dev-AR → prod-AR retag). The first iteration rebuilds for prod release tags with identical inputs; binary-identical promotion is a Phase-2 improvement, tracked as a follow-up.
- Tightening CSP to per-env hostnames (currently wildcard covers both). Decoupled, future change.
- Runtime feature flags or A/B config (this design adds *static* env config only; the same `/config.json` shape across all browsers in a given env).
- Migrating `import.meta.env.DEV` to runtime config — semantically wrong; those reads encode dev-server-vs-build, not K8s environment.
- Upstreaming the Aurelia plugin fix as a blocker. Filed in parallel; does not gate this change.

## Decisions

### D1. Replace build-time env bake with runtime `/config.json` fetched at bootstrap

**Chosen**: SPA fetches `/config.json` from same origin during `main.ts` bootstrap, before `Aurelia.start()`. Caddy serves the file from `/srv/config.json`; K8s mounts a per-env ConfigMap onto that path.

**Alternatives considered**:
- **A. Keep build-time bake, switch to `BUILD_TARGET` env var** (vite.config.ts reads custom env, ignores Vite mode for selection, keeps mode=`production`). Smallest patch. Rejected: still per-env images, doesn't eliminate the bug class — future build-time flags will reintroduce the same trap. The "spot-check verified env values, didn't verify templates" failure mode persists.
- **B. Keep build-time bake, use `.env.production.local` file swap in CI** (`cp .env.prod .env.production.local && vite build`). Rejected: uses Vite's `.local` convention against its semantic intent (developer-only overrides). Confusing for future contributors.
- **C. Caddy `envsubst` at container startup** to template `index.html` with env values from container env vars. Rejected: prevents Subresource Integrity / strict CSP without `unsafe-inline`, and adds a Caddy template plugin dependency. Worse than D1 for the same outcome.
- **D. Inject `window.__APP_CONFIG__` via `<script>` in index.html, rendered by Caddy at request time**. Rejected: same drawbacks as C, plus index.html caching becomes per-env (Caddy must not cache it).

D1 is the cleanest separation: image == code, ConfigMap == environment. ArgoCD natively reconciles ConfigMaps. Reloader auto-rollouts on change. Bootstrap fetch is intra-pod (~5ms).

### D2. Single image, env-agnostic; per-env divergence lives in K8s ConfigMap

**Chosen**: The Docker build accepts no env-specific build-args. `npm run build` produces one canonical bundle. Both `liverty-music-dev/frontend/web-app` and `liverty-music-prod/frontend/web-app` AR pushes use the same source build (rebuilt on each path due to GitHub Actions topology, but with identical inputs).

**Rationale**: The proximate cause of v1.0.0 being blank was build-time divergence interacting with a plugin's mode check. Eliminating divergence eliminates that whole interaction surface — including future analogous bugs we cannot enumerate today.

**Phase-2 follow-up**: switch the release-tag CI to retag the dev-AR image (`gcloud artifacts docker tags add`) into prod-AR instead of rebuilding. Achieves true binary-identical promotion. Deferred because it requires CI restructuring and the v1 fix doesn't need it.

### D3. `AppConfig` via Aurelia DI, loaded inside an async bootstrap

**Chosen**:
```ts
// src/config/app-config.ts
export const IAppConfig = DI.createInterface<AppConfig>('IAppConfig')
export interface AppConfig {
  environment: 'dev' | 'staging' | 'prod'
  apiBaseUrl: string
  zitadelIssuer: string
  zitadelClientId: string
  zitadelOrgId: string
  vapidPublicKey: string
  circuitBaseUrl: string
  previewArtistIds: string[]
  previewArtistNames: string[]
  logLevel: 'trace' | 'debug' | 'info' | 'warn' | 'error'
}
export async function loadAppConfig(): Promise<AppConfig> {
  const res = await fetch('/config.json', { cache: 'no-store' })
  if (!res.ok) throw new Error(`config.json fetch failed: ${res.status}`)
  return await res.json() as AppConfig
}

// src/main.ts (sketch)
async function bootstrap() {
  const config = await loadAppConfig()
  validateEnvironmentMatchesHost(config)  // see D7
  initOtel(config.apiBaseUrl)
  const au = new Aurelia()
  au.register(Registration.instance(IAppConfig, config))
  au.register(/* existing registrations */)
  au.app(AppShell).start()
}
bootstrap().catch(showStaticErrorPage)
```

**Alternatives considered**:
- **Synchronous `XMLHttpRequest`** to keep `main.ts` synchronous. Rejected: blocking the main thread for ~5ms is acceptable but using a deprecated sync API for code we are writing today is wrong.
- **Module-level top-level await** (`const config = await loadAppConfig()` at module scope). Rejected: top-level await complicates Vite chunking and HMR; explicit bootstrap function is clearer and testable in isolation.
- **Global singleton without DI** (`window.__appConfig`). Rejected: bypasses Aurelia's DI lifecycle, makes unit tests harder to isolate, and is harder to mock in Vitest.

### D4. Module-level reads of env are refactored to function-level / DI-resolved reads

`grpc-transport.ts`, `proof-service.ts`, `preview-artists.ts` currently read `import.meta.env.VITE_*` at module-eval time (top-level `const`). These execute at import time, which is before `bootstrap()`'s `await loadAppConfig()` resolves. To make config-after-bootstrap safe:

- `grpc-transport.ts`: export `createTransport(config: AppConfig)` factory; callers resolve `IAppConfig` and call the factory. (Or register the transport as a DI factory keyed on `IAppConfig`.)
- `proof-service.ts`: same pattern — `CIRCUIT_BASE_URL` becomes a class field initialized from `resolve(IAppConfig)`.
- `preview-artists.ts`: this is the trickiest because `PREVIEW_ARTIST_IDS` and `PREVIEW_ARTIST_NAME_MAP` are module-level exports consumed by lazy-loaded `welcome-route`. Since `welcome-route` is only instantiated AFTER bootstrap completes (router resolves the route lazily), its imports' top-level evaluation can safely read `getAppConfig()` from a non-DI synchronous accessor that throws if called before `loadAppConfig()` ran. Concretely: keep a `let _config` module-scoped in `app-config.ts`, populated by `loadAppConfig()`. Export `getAppConfig()` as a synchronous getter that throws if `_config` is null. `preview-artists.ts` module-level consts call `getAppConfig().previewArtistIds`. This works because the lazy route chunk only evaluates after `au.start()` has resolved the bootstrap promise.

This gives us DI ergonomics for services (idiomatic) AND safe module-const access for lazy code (pragmatic, with explicit failure mode if invariant is violated).

### D5. Caddy serves `/config.json` with no-cache headers; K8s mounts ConfigMap as a single-file volume

```caddyfile
:80 {
  root * /srv
  file_server
  try_files {path} /index.html

  @config path /config.json
  header @config Cache-Control "no-cache, no-store, must-revalidate"
  header @config Content-Type "application/json; charset=utf-8"

  @sw path /sw.js
  header @sw Cache-Control "no-cache"
  header @sw Service-Worker-Allowed "/"
}
```

K8s volume mount uses `subPath` so the ConfigMap key replaces only `/srv/config.json` without shadowing the rest of `/srv`:

```yaml
volumeMounts:
- name: runtime-config
  mountPath: /srv/config.json
  subPath: config.json
volumes:
- name: runtime-config
  configMap:
    name: web-app-runtime-config
```

**Reloader annotation** (`reloader.stakater.com/auto: "true"`) on the Deployment triggers a pod rollout when the ConfigMap changes. Reloader is already deployed in both clusters.

**Caveat**: `subPath` mounts do NOT auto-update on ConfigMap change (the file in the pod is a snapshot taken at mount time). Reloader's rollout addresses this. Without `subPath`, kubelet would atomically update the symlink but we'd lose the rest of `/srv`. The trade-off is correct: prefer explicit rollout (visible, ArgoCD-reconciled) over silent in-place file swap.

### D6. Service Worker bypasses precache for `/config.json`

Add an explicit `NetworkOnly` route in `sw.ts`:

```ts
registerRoute(
  ({ url }) => url.pathname === '/config.json',
  new NetworkOnly(),
)
```

Workbox's `precacheAndRoute(__WB_MANIFEST)` runs first and matches only `__WB_MANIFEST`-listed assets. `/config.json` is intentionally NOT in `__WB_MANIFEST` (it's not in `dist/`, it's mounted at deploy time). Adding the explicit NetworkOnly route is defense-in-depth against future Workbox runtime-caching defaults changing.

**SW offline behavior**: if the user is offline AND the app reloads, `/config.json` fetch fails → static error page. This is acceptable for a music-discovery PWA whose primary value is online. If offline-config becomes a requirement later, switch to `NetworkFirst` with a short TTL; the change is additive.

### D7. Environment cross-check at boot

`config.json` includes an `environment` field. At bootstrap, validate:

```ts
function validateEnvironmentMatchesHost(config: AppConfig): void {
  const host = window.location.hostname
  const expected = host === 'liverty-music.app' ? 'prod'
    : host === 'dev.liverty-music.app' ? 'dev'
    : host === 'staging.liverty-music.app' ? 'staging'
    : null  // localhost / preview deploys: skip check
  if (expected && config.environment !== expected) {
    throw new Error(
      `Config environment mismatch: host=${host} expects ${expected}, ` +
      `config.json says ${config.environment}. Likely a misconfigured ConfigMap mount.`,
    )
  }
}
```

This catches the failure mode where a prod pod accidentally serves the `public/config.json` shipped in the image (which contains dev values), by refusing to start instead of silently calling dev URLs from prod.

### D8. `public/config.json` is checked-in with dev values

The frontend repo's `public/config.json` is committed with dev environment values. This serves three purposes:

1. **Local dev** (`npm start`): Vite serves the public dir; the app reads dev values and connects to dev backend. Works out-of-the-box for any developer.
2. **Storybook / Playwright local runs**: same — dev values are accurate for these.
3. **Image fallback**: if the K8s ConfigMap mount somehow fails (operator error), the pod serves dev values. D7's cross-check then refuses to start in prod. Failure is loud, not silent.

This makes `public/config.json` effectively "the dev environment's config" — accurate, useful, and not a security issue because all values are public.

### D9. Phased delivery (single change, single PR per repo)

The change crosses three repos. Order:

1. `specification` PR with this change's artifacts → merge.
2. **In parallel** (after spec PR exists but before merge needed):
   - `frontend` branch with code refactor + Dockerfile + Caddyfile + public/config.json. CI rebuilds dev image successfully.
   - `cloud-provisioning` branch with ConfigMap overlays + Deployment patch.
3. Merge `cloud-provisioning` PR first → ArgoCD adds ConfigMap to dev cluster. Dev pod restarts (Reloader) with empty ConfigMap → falls back to image's `public/config.json` (dev values). Behavior unchanged.
4. Merge `frontend` PR → new dev image deployed; reads `/config.json` (now ConfigMap-backed). Dev verified.
5. Cut frontend release tag (e.g., `v1.0.1` or `v1.1.0`). Prod CI builds + pushes to prod-AR.
6. cloud-provisioning prod overlay updated with new image tag + prod ConfigMap. Manual `pulumi up --stack prod` if any IaC change (none expected). ArgoCD syncs prod.
7. Post-deploy smoke E2E runs against `https://liverty-music.app/`.

Rollback at any step: revert the offending repo PR. The change is additive in cloud-provisioning (adding ConfigMap doesn't break anything if the image isn't using it yet), so step ordering is forgiving.

### D10. Defense-in-depth: post-build template-presence assertion

Add `frontend/scripts/verify-build-templates.ts` invoked from CI after `npm run build`:

```ts
// Asserts that every route chunk contains template-derived strings.
// If a chunk has compiled successfully but its template was stripped
// (the regression class we just hit), this script fails.
const routeChunks = glob('dist/assets/*-route-*.js')
const requiredMarkers: Record<string, string> = {
  'welcome-route': 'welcome-hero',
  'dashboard-route': 'dashboard',
  // ... one well-known template-derived string per route
}
for (const [routePrefix, marker] of Object.entries(requiredMarkers)) {
  const chunk = routeChunks.find(c => c.includes(routePrefix))
  if (!chunk || !readFileSync(chunk, 'utf-8').includes(marker)) {
    throw new Error(`Route chunk for ${routePrefix} missing template marker '${marker}'`)
  }
}
```

This catches the specific regression that v1.0.0 hit AND any analogous future regression (HTML import path changing, plugin version bump, etc.). Runs in <100ms, no flakiness.

## Risks / Trade-offs

- **[Risk] Bootstrap-time `/config.json` fetch failure renders the app unable to start** → Mitigation: Caddy serves the file from the same pod (mount, not network), so failure modes are limited to ConfigMap mount errors caught at K8s reconciliation. The shape-validation in `loadAppConfig()` plus D7's environment cross-check fail fast with a static error page that tells the operator exactly what's wrong.
- **[Risk] PWA offline scenario: user with no network can't bootstrap** → Mitigation: explicit non-goal for this change. If/when offline-tolerant config is needed, switch SW route from `NetworkOnly` to `NetworkFirst` with a short TTL. Additive change.
- **[Risk] Module-level const reads in `preview-artists.ts` could break if a developer adds an early-import** → Mitigation: D4's `getAppConfig()` throws on premature access. The error message explicitly directs to `loadAppConfig()` in `main.ts`. Add a unit test that imports `preview-artists.ts` without bootstrapping and asserts the throw.
- **[Risk] ConfigMap content (committed to Git in `cloud-provisioning`) drifts from `.env` in frontend repo when developers add a new `VITE_*`** → Mitigation: TypeScript `AppConfig` interface is the source of truth. Schema validation in `loadAppConfig()` rejects missing-required-field at boot. CI runs the dev image against a dev ConfigMap pre-deploy; missing fields fail there.
- **[Risk] `subPath` ConfigMap mount caveat (no live update)** → Mitigation: Reloader annotation triggers explicit pod rollout. This is actually preferable (ArgoCD/audit-visible) to silent in-place file swap.
- **[Risk] Rebuilding for prod release means dev-built and prod-built images differ at the bit level (different timestamps, perhaps minor non-determinism in dependency order)** → Mitigation: functionally identical, since inputs (source + lockfile) are identical. Phase-2 follow-up addresses true bit-identity via dev-AR → prod-AR retag.
- **[Trade-off] Bootstrap adds one network round-trip before Aurelia.start()** → Cost: ~5ms intra-pod. Imperceptible. Could be avoided by inlining config into `index.html` (rejected in D1.C/D for index.html caching reasons).
- **[Trade-off] `public/config.json` contains dev hostnames committed to the repo** → No change vs. today (those values already in `.env` and `.env.prod`, all public per D3 of `prepare-prod-service-in`).
- **[Trade-off] Existing CSP is wildcard-broad to cover both envs** → Pre-existing condition. Tightening CSP requires either runtime CSP generation (Caddy template) or per-env image (which we're explicitly removing). Deferred.

## Migration Plan

**Pre-conditions** (verify before starting):
- `prepare-prod-service-in` change is acknowledged as superseded for its build-time bake portions (its prod-AR/Workload-Identity work remains in force).
- Reloader is healthy in both dev and prod clusters (`kubectl get pods -n reloader`).
- v1.0.0 prod is in current broken state (blank screen); no user impact to coordinate.

**Steps** (matches D9 ordering):

1. Merge `specification/adopt-runtime-config-for-frontend` PR.
2. Open `cloud-provisioning/adopt-runtime-config-frontend` PR adding:
   - `k8s/namespaces/frontend/overlays/dev/configmap.yaml`
   - `k8s/namespaces/frontend/overlays/prod/configmap.yaml`
   - Deployment patch (volumeMount + volume + Reloader annotation) under `base/web/deployment.yaml`.
3. Open `frontend/adopt-runtime-config` PR with code refactor + `public/config.json` (dev values) + Caddyfile + Dockerfile cleanup + post-build assertion script. Delete `.env.prod`.
4. Both PRs reviewed in parallel.
5. Merge `cloud-provisioning` PR first. ArgoCD applies; dev pod restarts via Reloader, picks up new ConfigMap. Dev still serves the OLD image (no `/config.json` reader yet). No visible change.
6. Merge `frontend` PR. Dev CI builds new image, pushes to dev-AR `:latest`. ArgoCD Image Updater bumps dev Deployment. New pod starts, fetches `/config.json`, app boots with runtime config. Verify dev `https://dev.liverty-music.app/` works.
7. Cut frontend release tag `v1.0.1` on the new merge commit. Release CI builds → pushes to `liverty-music-prod/frontend/web-app:v1.0.1`.
8. Update `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml` image pin to `v1.0.1`. Merge.
9. ArgoCD syncs prod. New pod fetches ConfigMap-backed `/config.json` (prod values). Verify `https://liverty-music.app/` renders.
10. Run post-deploy smoke E2E (Playwright) against prod URL.
11. Archive this change in OpenSpec; update specs/ tree.

**Rollback**:
- After step 5 (cloud-provisioning merged): trivial revert — image still old, ConfigMap unused.
- After step 6 (frontend merged to dev): revert frontend PR; dev pod redeploys old image. ConfigMap orphaned but harmless.
- After step 9 (prod): revert cloud-provisioning image pin to previous tag (whatever was working — but note v1.0.0 is broken, so there's no good earlier prod baseline to revert to; rollback in prod means "fix forward").

**Verification at each step**:
- Step 5: `kubectl describe configmap web-app-runtime-config -n frontend` shows expected data.
- Step 6: `curl https://dev.liverty-music.app/config.json` returns dev values; `dev.liverty-music.app` loads with expected dashboard content.
- Step 9: same against prod URL; environment field equals `prod`.

## Open Questions

1. **Should we file the upstream `@aurelia/vite-plugin` PR as a hard prerequisite or parallel deliverable?** → Recommended: parallel. This change doesn't depend on the upstream fix (we sidestep the bug entirely by keeping mode='production'). Upstream PR improves the ecosystem; merge timing is independent.

2. **Should the post-build template-presence assertion be a hard CI fail or a warning during a soak period?** → Recommended: hard fail from day one. The script is deterministic and the bug it guards against is severe (full-app failure). No reason to allow regressions through.

3. **Phase 2 timing for true binary-identical image promotion (dev-AR → prod-AR retag)** → Out of scope for this change. Track as a follow-up issue. Likely triggered by: staging environment introduction OR a security audit requiring "tested image == deployed image" attestation.

4. **Should the `circuitBaseUrl` be moved out of `AppConfig` since it's optional (some envs may not have ZK circuits)?** → Resolution: keep in `AppConfig` as required-string; for envs without circuits set to empty string and have `ProofService` no-op when empty. Simpler than optional-field handling and the value is always known at deploy time.

5. **How do we ensure the ConfigMap content stays in sync with the `AppConfig` TypeScript interface?** → Acceptable for v1: TypeScript interface is single source of truth, `loadAppConfig()` validates shape, missing fields fail loud on bootstrap. Long-term option (not in scope): generate a JSON Schema from TS and validate ConfigMap content in cloud-provisioning CI. Track as follow-up.
