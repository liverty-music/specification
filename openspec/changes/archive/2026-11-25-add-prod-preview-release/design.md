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

- **Fans see zero failed requests whenever a release goes live.** User experience is not traded for anything else in this change.
- By default a release goes live by itself, as soon as its automatic check on the preview address passes: the pin bump is still the deploy.
- When a release is risky, or the owner asks, the owner can use it in production on addresses fans do not use before any fan is served it, and then promote or abort it with one explicit action each.
- A check can be run by a person or by an agent with commands that only read.

**Non-Goals:**

- Metric-based automatic promotion or rollback. Traffic is a handful of requests; there is nothing to analyze beyond the smoke check.
- Percentage canaries as a goal in themselves. A release is either preview-only or serving everyone.
- Other workloads, and dev. They keep their current rollout.
- A separate preview database. Preview uses the production database.
- A new MCP server for Argo CD. `kubectl` and `argocd` are already installed and cover the reads.

## Decisions

### D1. Verification and cutover are separate; the cutover mechanism is chosen by measurement

**What failed.** The first implementation was an Argo Rollouts `blueGreen` Rollout through `workloadRef`, with an automatic pre-promotion smoke check. It gave the owner a preview, but promoting the `fan-api` Rollout answered `503` for 17 to 25 seconds in two measured runs (a request about every 0.2 seconds to the production API hostname). That breaks the first goal. `blueGreen` only moves Service selectors, so the new Pods join the fans' backend (a NEG with its own health check) at the moment of promotion. Argo Rollouts' own documentation says blue-green behind an L7 load balancer is "not supported without a chance of downtime" (written for AWS ALB; GKE's NEG shows the same symptom, which is consistent with the cause but not proven for this cluster).

**What is verified, from the primary sources.**

- Argo Rollouts issue `argoproj/argo-rollouts#4710` (open): on GKE with the Gateway API plugin and the *default* canary strategy, the last step produces `failed_to_pick_backend` 503s for 8 to 36 seconds. Its reporter's analysis: GCP health-checks each backend service independently, so the Pods that were healthy behind the canary backend must pass a fresh health check behind the stable backend after the stable selector flips. The cause is the reporter's, not confirmed by a maintainer.
- Argo Rollouts and the Gateway API plugin document `pingPong` as the remedy for selector swaps behind a load balancer: two persistent Services whose selectors never change, and the controller alternates which one is stable while the plugin shifts HTTPRoute weights. For plugin-based routers it needs Argo Rollouts v1.10 or later (the cluster runs v1.10.2). No page shows it on GKE Gateway.
- The plugin's provider table lists Google Cloud as tested only with plugin 0.2.0 and Gateway API 0.7.0 (current plugin releases need `gateway.networking.k8s.io/v1`).
- The plugin documents a separate HTTPRoute that sends a hostname only to the canary Service ("Advanced Deployments"), which is how a preview hostname is built with a plain canary. The `pingPong` page shows no equivalent, and there the canary role alternates between two Services.
- GKE documentation (Troubleshoot load balancing, Configure Gateway resources): 502/503 when Pods are removed are addressed with a connection draining timeout (`GCPBackendPolicy`, default 0), `preStop` of at least the drain timeout plus a drain latency (estimated at one minute) and `terminationGracePeriodSeconds` of at least the `preStop` time plus shutdown time; "configuring health checks won't prevent 502 errors". `HealthCheckPolicy` defaults: interval 5 seconds when a policy exists, thresholds 2.
- Not found in any GKE page read: what the `cloud.google.com/load-balancer-neg-ready` readiness gate (present on the Pods) guarantees during a rolling update, and whether the NEG controller behaves the same for Gateway and Ingress. The Ingress-era reports (`kubernetes/ingress-gce#1718`, `#638`) are hints only: #1718 attributes 502s on rolling deployments to the load balancer still sending to the terminating Pod, on Autopilot, and #638 reports 5 to 10 seconds of 502 after a Service selector switch.

**Candidates.**

| | Idea | Documented | Open |
|---|---|---|---|
| B | A second always-warm *candidate lane* (own Deployment, Service, preview route) per workload runs the candidate tag. Promotion is a git commit that bumps the stable tag, so fans get a normal rolling update (`maxUnavailable: 0`, `maxSurge: 1`) of the stable Deployment. | The drain, `preStop` and grace-period guidance above | Whether a tuned rolling update shows zero failures on this cluster (Autopilot node changes are reported to matter) |
| A' | Argo Rollouts `canary` with the Gateway API plugin and `pingPong`: selectors never change; promotion moves weights between two warm Services. | `pingPong` as the remedy; the plugin's route-weight management | No GKE Gateway example; how a preview hostname works when the canary role alternates; plugin maturity on GKE |

Rejected: `blueGreen` (measured, above); the default canary with the plugin (open GKE issue #4710); header or cookie canary (a browser cannot send a header, and a cookie loses to the fan web app's Service Worker, which serves the cached shell without reaching the Gateway); Flagger (a second controller that copies the Deployment, colliding with ArgoCD ownership); Kargo (promotes between environments, and dev is stopped); feature flags (switch code paths, so they cannot check a global stylesheet, a dependency update or startup code; they stay the tool for hiding one new screen). Google Cloud Deploy would replace the ArgoCD delivery path and is kept only as a fallback if both B and A' fail.

**Decision (2026-11-24): B, with `minReadySeconds`.** B was tried first because its experiment cannot touch fans: the candidate lane has its own preview hostname, so a rolling update can be measured there. Measured with the 8.2 probe from inside the cluster, five rolling updates per setting:

- With the drain settings of D9 alone, 4 of 5 updates answered `503` for 5 to 10 seconds, starting 3 to 6 seconds after the new Pod was Ready. The Pod events of every run show the cause: about 5 seconds after the Pod starts, the NEG readiness reflector reports "NEG is not attached to any Backend Service with health checking" and marks `cloud.google.com/load-balancer-neg-ready` true at once, so the gate does not wait for the load balancer (the same message appears in `kubernetes/ingress-gce#1718`); the old Pod is stopped about 6 seconds later; and the new endpoint needs about 19 seconds after its attach to pass the load balancer's health check (5 second interval, two successes, plus propagation).
- With `minReadySeconds: 45`, which keeps the old Pod until the new one has been Ready that long, all five updates showed zero non-2xx responses and zero client errors (3331 target requests, 3352 control requests).

So the readiness gate cannot be relied on for GKE Gateway NEGs in this cluster, and `minReadySeconds` (at least the health check's time to healthy, with room) is part of the mechanism. A' stays the documented fallback and was not needed. Section 9 (D10) moves the payout sweeper out of the fan API, and task 8.6 replaces the Rollouts, one workload at a time, with this mechanism.

**Measurement criterion (both candidates).** A request about every 0.1 seconds, sent from a Pod in the cluster to the public hostname, across at least five releases: zero responses with status 500 or above. A client-side timeout counts only when the same loop against an untouched hostname shows none: from the maintainer's WSL machine an untouched host timed out on about a fifth of the requests, so timeouts measured there are not evidence.

**The default and the hold.** By default a release goes live by itself after the automatic check passes. A release is held for the owner only when it is risky or the owner asks. Under B, a GitHub pre-release bumps only the candidate tag, and promotion is a workflow that copies the candidate tag to the stable pin. Under A', a held release sets `autoPromotionEnabled: false` before it is cut. The first implementation already runs this way (automatic check, then promotion), and that behavior stays the target.

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

*Applies only while a Rollout manages Service selectors (the first implementation, or A'). Under B nothing but ArgoCD touches a Service, and this decision disappears. Task 6.2 showed the ignore held across a pause and a promote.*

Rollouts injects a hash of the ReplicaSet into the selector of the active and preview Services. The Argo Rollouts docs do not say whether Argo CD reports that as drift, and both prod Applications (`backend`, `frontend`) run with `selfHeal: true` (`k8s/argocd-apps/prod/backend.yaml`, `frontend.yaml`): a selector Argo CD treats as drift would be reverted, which removes the hash and lets the active Service select both ReplicaSets while a release waits.

So the change does not wait to observe drift. When a Rollout is added (tasks 5.1 and 5.2), its Application gets `ignoreDifferences` for `/spec/selector` of that Rollout's active and preview Services (the mechanism `backend.yaml` already uses for the KEDA-driven replicas of `event-consumer`) and the sync option `RespectIgnoreDifferences=true`, the documented Argo CD pattern for a field a Rollout changes (shown in the Argo Rollouts docs for Istio route weights). Applying it to the selector is an inference from that pattern; task 6.2 confirms it holds during a pause. `fan-api-webhook-svc` is not managed by the Rollout (D8) and keeps its selector in git.

### D6. The check is the existing smoke spec plus read-only commands

Run `SMOKE_BASE_URL=https://preview.liverty-music.app` through the existing `post-deploy.spec.ts` (it catches blank pages and lost styles). API checks are `curl` calls against `https://api.preview.liverty-music.app`. State is read with `kubectl get rollout -o json`, `kubectl describe rollout` and `argocd app get`. Argo CD bundles resource actions for `Rollout`: its documentation lists `abort`, `pause`, `promote-full`, `restart`, `resume` and `retry` for version 3.4 (Argo CD docs, "Resource Actions"). The Argo Rollouts FAQ lists only `resume` and `restart` and is out of date. The list differs between Argo CD versions, so task 6.1 lists the actions the pinned Argo CD offers (`argocd app actions list`) and records which one promotes a blueGreen pause and which one aborts. Both run through `argocd`, which is already installed. The `kubectl argo rollouts` plugin (`promote`, `abort`) is the fallback, added to the cloud-provisioning mise config only if an action is missing. An abort is followed by a `git revert` of the pin commit. While a rollout is paused, Argo CD shows the Application as Suspended (Argo Rollouts docs, "FAQ").

An agent runs the reads and the smoke spec and reports. By default the automatic check promotes; for a held release the owner says when to promote. No MCP server is added.

### D7. Order of rollout: both behind Rollouts first, `fan-web` before `fan-api`, then the releases

Both workloads are put behind Rollouts on their unchanged pins before any release goes through them. `fan-web` comes first: it is stateless and static, so it proves the controller, the routes, the certificates and the Deployment-at-zero setup with the least risk. `fan-api` follows, so that `api.preview` exists whenever a preview web app is checked (the web app calls it, D3). Releases then go through `fan-web` and then `fan-api`. A release that changes both is promoted API first, then web, because a new web app must work against the API that is already serving fans.

### D8. The webhook Service follows the active `fan-api` Pods only

*Under B the candidate lane's Pods carry a different `app` label, so `fan-api-webhook-svc` (selecting `app: fan-api`) never reaches them and the `role` labels are not needed.*

`fan-api-webhook-svc` selects Pods by `app: fan-api` alone (`k8s/namespaces/backend/base/fan-api/service-webhook.yaml`). A Rollout manages the selectors of its active and preview Services only, so during a pause this Service would also select the preview Pod, and a release nobody has checked would receive real Stripe webhooks and Zitadel action calls (`/pre-access-token`, `/account-login-event`). An aborted release would already have handled them.

The `fan-api` Rollout therefore labels its Pods through `activeMetadata` (`role: active`) and `previewMetadata` (`role: preview`), and the prod overlay adds `role: active` to the webhook Service's selector (Argo Rollouts docs, "Ephemeral Metadata": the preview ReplicaSet's Pods carry the preview labels, and on promotion the Pods are relabeled in place). Dev is unchanged. The same check covers every other Service that selects `fan-api` Pods: each must be the active or the preview Service, or select `role: active`.

### D9. Drain settings follow the GKE guidance, whichever mechanism wins

Every candidate removes Pods behind a NEG at some point (a rolling update's old Pod, or the previous ReplicaSet), and GKE's documentation attributes 502 and 503 at that moment to a missing drain: the load balancer keeps sending to an endpoint that has already been removed. The guidance is a connection draining timeout on the backend service, a `preStop` of at least that timeout plus a drain latency (estimated at one minute), and a `terminationGracePeriodSeconds` of at least the `preStop` time plus shutdown time. The cluster does not meet it today: `fan-api` drains for 60 seconds (`GCPBackendPolicy`) but its `preStop` sleeps 5 seconds, and `fan-web` has no `GCPBackendPolicy` (so a drain timeout of 0, the default) and no `preStop`. The health check alone does not prevent these errors, according to the same page.

Task 8.1 sets these values for both workloads before any measurement, so a failed measurement cannot be blamed on a setting the documentation already names. The exact values are chosen against the measured request duration (the GKE page suggests a drain of 1.5 to 2 times the longest request); the Connect handler timeout is 30 seconds (`SERVER_HANDLER_TIMEOUT`), so the 60-second drain stays.

**Scope: every workload behind the load balancer.** The NEG readiness gate does not wait for the load balancer anywhere in this cluster, so `admin-console-web`, `organizer-console-web`, `reception-web`, `admin-console-api`, `organizer-console-api` and `reception-api` have the same rolling-update gap as `fan-web` (found as five 503 responses at `admin.liverty-music.app` when ArgoCD rolled them together with `fan-web`). They get the settings measured on `fan-web` in their base, with no candidate lane: `minReadySeconds: 45`, `maxUnavailable: 0` with `maxSurge: 1`, a `GCPBackendPolicy` draining 30 seconds (web) or 60 seconds (API), a native `preStop` sleep of 90 seconds (web) or 120 seconds (API) and a `terminationGracePeriodSeconds` of 120 or 190 (the API's `SHUTDOWN_TIMEOUT` is 60 seconds, from `fan-api-config`), and an explicit `HealthCheckPolicy` (interval 5 s, thresholds 2). The release probe gets a `health` mode for the APIs, whose business RPCs answer 401 without a token. Zitadel (`auth.liverty-music.app`) sits behind the same load balancer and has the same gap; it is outside this change.

### D10. The settlement payout runs as a scheduled workflow in the workflow worker, not in the fan API

The settlement payout sweeper (`startSettlementSweeper`, every 5 minutes) starts inside every fan API process (`RunsPaymentSweepers()` is true for the `fan` workload) with the production Stripe key. It creates Stripe Transfers for held settlements whose release gate (event start plus the dispute buffer) has passed and whose Organizer's payout account is active. It is idempotent across Pods (a status guard in `MarkReleased`), so running copies is safe. But a periodic payout job inside the process that serves requests means that the number of API Pods is the number of payout runners, that every API rollout and every preview or candidate Pod carries the payout job (a held `fan-api` release would run unreviewed code with it), and that the payout capability sits on the public-facing process.

The repository already runs periodic work outside the API: six Kubernetes CronJobs that start workflows, and the workflow worker, which registers DBOS scheduled workflows with cron expressions (`internal/infrastructure/workflow/admin.go`: a report every 5 minutes, a retention sweep daily). The lottery draw and its issuance already moved from the API to the worker, and the worker already loads `api-stripe-secrets`. The settlement sweeper is the last periodic job left in an API process.

**Decision.** Register a DBOS scheduled workflow in the worker that calls `SettlementUseCase.ReleaseDueSettlements` every 5 minutes (`0 */5 * * * *`, the seconds field included), and remove the sweeper from the API wiring. The use case and its spec (`components/usecase/settlement/release-due-settlements`) do not change; only where it is triggered does. A DBOS schedule gives one run per tick across the cluster, durability and retries, and a place in the workflow list that the existing admin report already watches.

**Alternative.** A Kubernetes CronJob that runs the use case. Rejected: the existing CronJobs start workflows and do not do the work themselves, a CronJob adds a Pod per tick and one more image entry to bump, and the worker already holds the secrets and the schedule mechanism.

**Order.** (1) Release the backend with the scheduled workflow while the API sweeper still runs (two runners are safe because a release is idempotent) and confirm the ticks in the worker. (2) Release the backend without the API sweeper. (3) Remove the payout as a reason for the restriction on holding `fan-api` releases in the runbook, AGENTS.md and `candidate.yaml`; the restriction itself ends with task 8.6.

## Risks / Trade-offs

- **A single replica can still answer 503 at a release (measured 2026-11-25).** After two releases, GKE Autopilot's node scale-down evicted the fresh Pod (event `deleting pod for node scale down`) and, with one replica and no PodDisruptionBudget, nothing served until the replacement was Ready (16 s on `fan-web`, 25 responses). `minReadySeconds` and the drain settings do not touch this. `fan-web` therefore runs two replicas with a soft hostname spread and a `minAvailable: 1` PodDisruptionBudget (decided by the owner). `fan-api` stays at one replica because two Pods do not fit the `db-f1-micro` connection budget (21 of 22 usable in use; a pool of 2 leaves one request connection beside the DBOS LISTEN connection and a pool of 3 exceeds the budget, with up to four Pods' pools alive during a release): tracked in cloud-provisioning#823. The console web apps and APIs keep one replica, so a release or an eviction can still cost them a few seconds of 503.

- [The database is shared by preview and by the release fans use] → While a release waits, new-schema migrations run under the old code. Migrations stay backward compatible (expand, then contract in a later release); the runbook says so, and a paused release should not wait long.
- [A forgotten pause leaves fans on the old release, delaying a fix] → The runbook lists `kubectl get rollout` as the first check after any pin bump. Whether to add an ArgoCD notification for a paused rollout is left open below.
- [Argo CD shows the Application as Suspended while a release waits] → Anything that waits for the Application to be Healthy waits until the promotion; the runbook says so.
- [The webhook Service briefly has no endpoints when the Rollout is first introduced, or while the labels change on promotion] → Production has no users beyond the owner and one tester, so a short gap is acceptable; tasks 5.2 and 6.3 read the Service's endpoints before and after each change.
- [Preview writes real data in production] → The owner checks with their own account; the runbook names the account as the only one used on preview.
- [Preview events enter production analytics] → Events carry the same release version as the stable Pods, so they cannot be told apart by version. The owner's person gets the PostHog person property `$internal_or_test_user: true`, which puts it in the existing cohort `Internal / Test users`, the project's test-account filter. The frontend's `internalTrafficUserIds` allowlist (runtime `/config.json`) stays empty, because the repositories are public and a user id must not be written into them. Task 4.3 sets the property before preview is used.
- [Push subscriptions are per origin] → A subscription made on preview is a second, real subscription for that account; deleting it is part of the runbook's cleanup.
- [Cutover errors for fans] → Not accepted. The first implementation's 17 to 25 seconds of `503` (task 6.3) are replaced by the measured mechanism of D1; the criterion is zero responses of 500 or above across at least five releases (tasks 8.3, 8.5, 8.6).
- [The fan API process carries a periodic job: the settlement payout sweeper] → Removed by D10 (section 9): the payout runs as a schedule of the workflow worker since backend v1.142.0, so no API, preview or candidate Pod carries a payout job. A `fan-api` release is still not held for a manual look until task 8.6, for another reason: while the candidate lane exists, `api.preview` serves it (it follows the shared pin), not the Rollout's held Pods.
- [A configuration-only change does not go through the candidate] → Under B the candidate and stable lanes share ConfigMaps and Secrets, so such a change reaches both at once. Under the first implementation Reloader made it a new, gated revision. Configuration changes were never gated before this change.
- [Measurement noise] → Requests from a laptop timed out on unrelated hosts; the criterion in D1 counts server responses and measures from inside the cluster.
- [Autopilot cost of a second Pod during a pause] → One extra small Pod per workload, only while a release waits.
- [The Rollouts controller is a new cluster component] → Argo CD understands the health of a `Rollout` through its bundled Lua health check (Argo Rollouts docs, "FAQ"), the chart is pinned like the other charts, and reverting the commit that added the `Rollout` returns to today's behavior (it restores the Deployment's replicas too).

## Migration Plan

1. Done: release the frontend loader change (it is inert on every address but the preview one); install the Rollouts controller; provision the two hostnames, the Zitadel redirect addresses and the CORS origin; put `fan-web` and `fan-api` behind `blueGreen` Rollouts with an automatic pre-promotion check (tasks 1 to 7).
2. Tune drain settings, build the measurement, and measure B on a candidate lane at the preview hostnames, with no change to the fans' path (tasks 8.1 to 8.4). If B fails, measure A' on a test hostname (task 8.5).
3. Move the settlement payout sweeper into the workflow worker (section 9) before the first held `fan-api` release.
4. Replace the Rollouts with the winner, one workload at a time (`fan-web` first), and without a gap for fans. The Service of a Rollout carries a selector the controller wrote, so removing the Rollout and starting the plain Deployment would leave fans without a healthy endpoint for the time the new endpoint needs to pass the load balancer's health check (about 19 seconds, measured in task 8.3). The route-level switch has no such wait between backends that are already warm, so it bridges the move:
   1. The candidate lane runs and is warm (minutes of preview traffic).
   2. The fans' route lists both Services as backends and gives the candidate lane's Service the whole weight (the same image); the stable Service stays listed with weight 0, so its backend stays programmed and health-checked while it carries nothing.
   3. The Rollout, the analysis template, the Rollout's preview Service and the ArgoCD `ignoreDifferences` are removed, and the base Deployment runs plainly (1 replica, `minReadySeconds`, the drain settings). Fans stay on the candidate lane meanwhile.
   4. Once the new stable Pod is healthy behind its backend (read per endpoint from the Compute API, `networkEndpointGroups.listNetworkEndpoints` with `healthStatus: SHOW`, because `backend-services get-health` returns nothing for a backend at weight 0 even though its endpoints are still health-checked (observed on 2026-11-25); at least `minReadySeconds` after it is Ready), the weights are swapped back: the stable Service gets the whole weight.
   The 8.2 probe runs across each of the steps 2 to 4; any response of 500 or above stops the move.
5. Make the pins independent (candidate and stable) and the promotion a workflow, as task 8.6 says.

Rollback of the first implementation: abort a pending release; or revert the commit that added the `Rollout`, the preview Services and the routes, which also restores the Deployment's replica count so it serves again. Rollback of the replacement: revert its commit; the preview hostnames stay.

## Open Questions

- Should ArgoCD notify (the existing notification templates) when a held release waits for promotion? It can be added after the first real held release shows whether it is needed.
- Under A', how is a preview hostname built when the canary role alternates between ping and pong (task 8.5 answers it, or A' is dropped).
- Does the GKE NEG controller behave the same for Gateway as for Ingress (the Ingress-era reports are hints only). The measurements make this moot unless B fails.
