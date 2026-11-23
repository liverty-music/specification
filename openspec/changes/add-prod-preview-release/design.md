## Context

See proposal.md for why. What exists today, checked in the code:

- A release reaches production as one automated path: `bump-prod-pin` rewrites the image `newTag` in the prod overlays and pushes to `main`; ArgoCD auto-sync rolls the Pods. No step waits for a person (`cloud-provisioning/.github/workflows/bump-prod-pin.yml`).
- Traffic enters through one Gateway (`gke-l7-global-external-managed`); each workload has an HTTPRoute selected by hostname. Every public hostname has its own DNS record, Certificate Manager certificate and CertificateMapEntry, declared as one `{ name, subdomain }` entry in the catalog of `src/gcp/components/network.ts`. There is no wildcard certificate.
- Existing names put a console's API under `api.<console>` (`api.admin`, `api.organizer`, `api.reception`).
- `fan-api` and `fan-web` each run 1 replica in production.
- The fan web app loads `/config.json` (a ConfigMap) at startup. It holds `apiBaseUrl` and the environment, and the loader checks the environment against the page's host (`shared/config/known-hosts.ts`). A Service Worker is registered in production.
- Sign-in is the shared hosted login at `auth.liverty-music.app`; the fan application's redirect addresses are listed in `src/zitadel/components/frontend.ts`.
- Backend CORS origins are `CORS_ALLOWED_ORIGINS`, a list read from the environment.
- The frontend already has a Playwright post-deploy smoke spec driven by `SMOKE_BASE_URL` (`e2e/smoke/post-deploy.spec.ts`), which checks that the welcome page renders with its own styles.
- Dev is stopped indefinitely, and production has no users beyond the owner and one tester (CLAUDE.md, "Current operating state").

## Goals / Non-Goals

**Goals:**

- The owner can use a new `fan-web` and `fan-api` release in production, on addresses fans do not use, before any fan is served it.
- Promoting and aborting are one explicit action each; nothing promotes on its own.
- A check can be run by a person or by an agent with commands that only read.

**Non-Goals:**

- Metric-based automatic promotion or rollback. Traffic is a handful of requests; there is nothing to analyze.
- Percentage canaries. A release is either preview-only or serving everyone.
- Other workloads, and dev. They keep their current rollout.
- A separate preview database. Preview uses the production database.
- A new MCP server for Argo CD. `kubectl` and `argocd` are already installed and cover the reads.

## Decisions

### D1. Argo Rollouts `blueGreen` through `workloadRef`, in the prod overlay only

A `Rollout` in the prod overlay references the existing base `Deployment` with `workloadRef`, so the base manifests, the dev overlays and the existing prod patches (image tag, version label, the `TELEMETRY_SERVICE_VERSION` env) stay as they are. `autoPromotionEnabled: false` pauses the rollout once the new ReplicaSet is ready; the `previewService` points at the new Pods and the `activeService` at the current ones. `previewReplicaCount: 1` keeps the preview at one Pod.

Alternatives:

- **Header or cookie canary** (Argo Rollouts Gateway API plugin, Flagger): rejected. A browser cannot send a header, and a cookie loses to the fan web app's Service Worker, which serves the cached shell without reaching the Gateway. The Gateway API plugin also supports only canary (as documented by the plugin), and it is an alpha plugin mechanism.
- **Flagger**: built for metric-gated automatic canaries and copies the Deployment into primary and canary, which collides with ArgoCD ownership.
- **Google Cloud Deploy**: would replace the ArgoCD delivery path.
- **Kargo**: promotes between environments; with dev stopped there is no upstream stage.
- **A hand-made second Deployment per workload**: re-implements scale-up, the pause, the switch and the scale-down that Rollouts already does.
- **Feature flags** (PostHog, already wired): switch code paths, so they cannot check a global stylesheet, a dependency update or startup code. They stay the tool for hiding one new screen.

`blueGreen` only swaps Service selectors, so no traffic-router plugin is installed.

### D2. Preview is a subdomain pair: `preview.liverty-music.app` and `api.preview.liverty-music.app`

A subdomain is a separate origin: the Service Worker, the PWA install state, storage and the layout all behave as in production, and the address opens in any browser, on Android included.

Alternatives: a path prefix (`/preview/`) breaks the SPA's base path, asset paths, Service Worker scope and sign-in callbacks; `preview-api.*` and `preview.api.*` do not follow the existing `api.<console>` order. Two catalog entries, `{ name: 'fan-preview-web', subdomain: 'preview' }` and `{ name: 'fan-preview-api', subdomain: 'api.preview' }`, provision the DNS record, certificate and map entry. Production only: dev is stopped and keeps no preview.

The preview route for the API exposes only the fan API's own server port. It never routes `fan-api-webhook-svc`, so neither the Stripe webhook nor the internal Zitadel action endpoints are reachable on the preview address (same rule as the existing route's comment).

### D3. The fan web app chooses its API address from the page's address

The runtime configuration loader (`shared/config/app-config.ts`) overrides `apiBaseUrl` with `https://api.preview.liverty-music.app` when the page host is exactly `preview.liverty-music.app`, and `KNOWN_HOSTS` maps that host to `prod`. The value of `apiBaseUrl` in `/config.json` stays the default for every other host.

Why not a second ConfigMap: during the pause the new Pods serve the preview address, and after promotion the same Pods serve the production address. Their ConfigMap cannot differ between the two, so the choice has to be made from the address at run time. The loader is shared by the admin and organizer apps, but the rule matches one host and changes nothing for them.

Values the web app reads are unchanged; no RPC response field is added.

### D4. Sign-in and CORS accept the preview address

- Zitadel: the preview address's `/auth/callback` and `/auth/passkeys-callback` are added to `redirectUris`, and `https://preview.liverty-music.app/` to `postLogoutRedirectUris`, of the existing fan application in `src/zitadel/components/frontend.ts`, for production only. No new client.
- Passkeys are registered for the hosted login's own domain, so a passkey the owner already has should work from the preview address. This is inferred from how WebAuthn relying-party IDs work, not observed here; task 7.2 checks it with a real sign-in.
- CORS: `https://preview.liverty-music.app` is added to the production `CORS_ALLOWED_ORIGINS`. The stable API then also accepts that origin, which allows only a page the owner serves.

### D5. ArgoCD and Rollouts agree on who owns the Service selectors

Rollouts writes a pod-template-hash into the selector of the active and preview Services. ArgoCD would report that as drift. Task 5.3 observes whether it does with the cluster's server-side diff; if it does, the Services get an `ignoreDifferences` entry for `/spec/selector`. The fix is added only if the drift is seen.

### D6. The check is the existing smoke spec plus read-only commands

Run `SMOKE_BASE_URL=https://preview.liverty-music.app` through the existing `post-deploy.spec.ts` (it catches blank pages and lost styles). API checks are `curl` calls against `https://api.preview.liverty-music.app`. State is read with `kubectl get rollout -o json`, `kubectl describe rollout` and `argocd app get`. Promoting is `kubectl argo rollouts promote <name>` or the Argo CD resource action; task 5.2 settles which one works and adds the plugin to the cloud-provisioning mise config only if needed. Aborting is `kubectl argo rollouts abort <name>` followed by a `git revert` of the pin commit.

An agent runs the reads and the smoke spec and reports; the owner promotes. No MCP server is added.

### D7. Order of rollout: `fan-web` first, then `fan-api`

`fan-web` is stateless and static, so it proves the install, the routes, the certificates and the selector question with the least risk. `fan-api` follows once those hold. A release that changes both is promoted API first, then web, because a new web app must work against the API that is already serving fans.

## Risks / Trade-offs

- [The database is shared by preview and by the release fans use] → While a release waits, new-schema migrations run under the old code. Migrations stay backward compatible (expand, then contract in a later release); the runbook says so, and a paused release should not wait long.
- [A forgotten pause leaves fans on the old release, delaying a fix] → The runbook lists `kubectl get rollout` as the first check after any pin bump. Whether to add an ArgoCD notification for a paused rollout is left open below.
- [Preview writes real data in production] → The owner checks with their own account; the runbook names the account as the only one used on preview.
- [Preview events enter production analytics] → Events carry the same release version as the stable Pods; the owner's identity is already marked internal by the analytics service, which keeps them out of fan metrics.
- [Push subscriptions are per origin] → A subscription made on preview is a second, real subscription for that account; deleting it is part of the runbook's cleanup.
- [Selector switch lag behind the load balancer] → `scaleDownDelaySeconds` keeps the old Pods up after the switch; task 6.2 measures failed requests across a promote.
- [Autopilot cost of a second Pod during a pause] → One extra small Pod per workload, only while a release waits.
- [The Rollouts controller is a new cluster component] → Argo CD ships a built-in health check for `Rollout`, the chart is pinned like the other charts, and removing the `Rollout` and restoring the `Deployment` returns to today's behavior.

## Migration Plan

1. Release the frontend loader change (it is inert on every address but the preview one).
2. Install the Rollouts controller; provision the two hostnames, the Zitadel redirect addresses and the CORS origin.
3. Put `fan-web` behind a `Rollout`; run a no-op release through it to prove pause, preview, promote and abort.
4. Do the same for `fan-api`.

Rollback: abort a pending release; or delete the `Rollout` and the preview Services and routes, which makes the `Deployment` serve again. Nothing in the base or dev changes, so no other rollback is needed.

## Open Questions

- Should ArgoCD notify (the existing notification templates) when a `Rollout` pauses for promotion? It does not change the specs or the tasks above; it can be added after the first real release shows whether it is needed.
