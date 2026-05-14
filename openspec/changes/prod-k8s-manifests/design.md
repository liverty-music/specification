## Context

After the just-merged `migrate-prod-to-autopilot` change, the prod cluster (`autopilot-cluster-osaka` in `liverty-music-prod`) is live and idle: Autopilot has provisioned zero nodes, kube-state-metrics is uninstalled (per the `enableComponents: [SYSTEM_COMPONENTS]` minimum), and no application traffic flows. The Cloud DNS A records for `api.liverty-music.app` and `auth.liverty-music.app` resolve to `34.110.151.208` (the `api-gateway-static-ip` global address), but that IP is `RESERVED` (unbound) — no Gateway is claiming it.

Meanwhile, dev's full manifest set lives at `k8s/argocd-apps/dev/` (14 ArgoCD Applications) and `k8s/namespaces/<ns>/overlays/dev/` (11 namespaces, each with a `dev/` overlay). Prod has only `k8s/namespaces/argocd/overlays/prod/` (created preemptively pre-cluster). The mission: author the missing 10 overlays + 14 prod Applications, plus the Gateway+HTTPRoute that claims the static IP, plus opt-in PodMonitoring CRDs.

The team's plan: after prod is fully bootstrapped and externally addressable, retire the dev cluster. This transfers the full GKE free-tier credit onto prod (the savings the migrate change unlocked). This change is the blocker.

## Goals / Non-Goals

**Goals:**

- Bring prod cluster from "infra-only, idle" to "ArgoCD-managed, externally addressable, Zitadel-served" in a single coherent PR.
- Mirror the dev manifest set structurally (same 14 Apps, same per-namespace overlay shape) but with prod-specific patches: hostnames, ESC secret references, resource limits, PodMonitoring opt-in.
- Bind the existing `api-gateway-static-ip` (`34.110.151.208`) to a prod Gateway so the pre-existing DNS records (`api.liverty-music.app`, `auth.liverty-music.app` → that IP) start resolving.
- Lock in the Spot label invariant — every Pod template in prod overlays carries `cloud.google.com/gke-spot: "true"`. Extend the lint target to render *both* dev and prod overlays.
- Opt application metrics into GMP explicitly via per-workload PodMonitoring CRDs with tight `metricRelabeling` keep-rules. Avoid the "discover everything" auto-monitoring path Autopilot disabled.
- Capture self-hosted Zitadel for prod as part of this change (not a follow-up), reusing the dev runtime/lifecycle pattern but scoped to prod GSM secrets + prod Cloud SQL.

**Non-Goals:**

- Retiring the dev cluster. That's a separate operational decision after prod is verified working. This change is the *enabler* but doesn't trigger the retirement.
- Blockchain workloads (testnet/mainnet smart-contract interaction, signing keys). Deferred to a `prod-blockchain-workloads` change when the testnet phase begins.
- Multi-region / DR setup. Single-region prod stays the design until SLO-driven demand arises.
- Application code changes. Backend/frontend manifests reference the existing built images; no code edits in `backend/` or `frontend/` repos.
- Rewriting any namespace's base manifests. This change is *additive* (new prod overlays) — bases stay untouched.

## Decisions

### D1: Mirror dev's manifest structure 1:1 — same Apps, same namespace count

**Decision:** Author `k8s/argocd-apps/prod/` with 14 ArgoCD Applications matching dev's 14 (`argocd`, `atlas-operator`, `backend-migrations`, `backend`, `cluster`, `external-secrets`, `frontend`, `gateway`, `keda`, `namespaces`, `nats`, `otel-collector`, `reloader`, `zitadel`). Author 10 missing namespace `prod/` overlays. Do not subset.

**Why:**

- Operationally, having dev and prod look structurally identical means a fix in one place can be propagated to the other mechanically; subsetting prod creates an irreversible "what's missing here" cognitive tax.
- The 14 dev Apps are tightly integrated — most depend on shared infrastructure (`namespaces`, `external-secrets`, `reloader`). Picking a subset triggers a dependency tree analysis that's more work than just shipping all 14.
- Autopilot bills only for what's actually scheduled. Pods that don't have traffic don't cost anything at idle (Pending stays Pending). So shipping the full set has near-zero baseline cost until traffic arrives.

**Alternative considered:** ship just `argocd` + `external-secrets` + `backend` + `frontend` (~4 Apps). Rejected because the missing pieces (`reloader`, `keda`, `atlas-operator`, `nats`, `otel-collector`, `gateway`) all have transitive dependencies from the 4 Apps — leaving them out breaks reconciliation.

### D2: Per-namespace overlay shape — kustomize patches limited to env-divergent fields

**Decision:** Each `k8s/namespaces/<ns>/overlays/prod/kustomization.yaml` extends the base with `prod`-specific patches limited to:

1. **ExternalSecret refs**: change `secretStoreRef.name` from `google-secret-manager-dev` to `google-secret-manager-prod` (or equivalent) so the ESO controller pulls from the prod ESC environment.
2. **Hostname patches**: `api.dev.liverty-music.app` → `api.liverty-music.app`, `auth.dev.liverty-music.app` → `auth.liverty-music.app`. Applied via JSON-patch to ConfigMap data and HTTPRoute hostnames.
3. **Image tag**: same images, same tags — no env-divergent images. ArgoCD Image Updater handles tag bumps across both envs.
4. **Resource requests/limits**: same as dev for now (no SLO-driven sizing yet). When real prod traffic arrives, a `right-size-prod` follow-up change tunes these.
5. **Spot label**: confirmed via lint — base manifests already include it for dev, so prod inherits unchanged.

**Why limited patches:** the more divergent the overlays, the more divergent the runtime behavior. The team should be able to debug prod issues by reading dev manifests; that only works if prod and dev are mostly identical.

**Alternative considered:** prod gets bigger resource limits (CPU/memory headroom) from day 1. Rejected — without real load data, we'd be guessing. Stick with dev sizing, profile prod under real load, then tune.

### D3: Gateway static-IP binding — declarative `addresses` field on Gateway CR

**Decision:** The prod Gateway CR's `spec.addresses` includes:

```yaml
addresses:
  - type: NamedAddress
    value: api-gateway-static-ip
```

This tells GKE to bind the Gateway to the existing `api-gateway-static-ip` global address (currently `RESERVED`, value `34.110.151.208`). On ArgoCD sync, the Gateway claims the IP and the existing Cloud DNS A records start resolving live.

**Why declarative:** the alternative (provisioning a fresh static IP per Gateway sync) would break the pre-existing DNS records that the migrate change pinned. By using `NamedAddress`, GKE looks up the existing global address by name and binds without reallocating.

**Risk**: brief window during the first ArgoCD sync where the Gateway is being created but hasn't yet claimed the IP. DNS records resolve to an IP no one is listening on → user-visible 503. Mitigation: this only matters under real traffic; prod has none yet. The window closes in seconds.

**Alternative considered:** provision a fresh static IP via Pulumi, update DNS records, retire the old IP. Rejected — three coordinated changes (Pulumi, DNS, Gateway sync) vs one (Gateway sync claims existing IP). The migrate change deliberately preserved the IP to avoid this dance.

### D4: Self-hosted Zitadel for prod — reuse dev lifecycle, swap secret namespace + DB

**Decision:** The `k8s/namespaces/zitadel/overlays/prod/` overlay reuses dev's runtime shape (same image, same readiness/liveness probes, same masterkey-immutability pattern) but patches:

- `ZITADEL_DATABASE_POSTGRES_HOST` → prod Cloud SQL PSC endpoint
- `ZITADEL_DATABASE_POSTGRES_USER` → `zitadel` IAM SQL user in prod
- Mounted secret: `zitadel-machine-key` and `zitadel-login-pat` from `liverty-music-prod` GSM (via ExternalSecret with the prod-scoped SecretStore)
- `ZITADEL_API_URL` → `https://auth.liverty-music.app`
- `ZITADEL_ISSUER` → `https://auth.liverty-music.app`

**Pulumi-side change:** remove the `environment === 'prod'` gate around `zitadelMachineKey` / `zitadelLoginPat` ESC reads at `src/index.ts:73`. After removal, those ESC values flow through to Pulumi-managed GSM Secret resources for prod. Seed values via `esc env set liverty-music/prod pulumiConfig.zitadel.zitadelMachineKey ...` before merge.

**Bootstrap chicken-and-egg**: per memory `reference_zitadel_bootstrap_uploader_scenario_2.md`, the bootstrap-uploader sidecar only fires on first-instance Zitadel boot. For prod's first deploy, the admin SA key needs a one-shot manual seed into the `zitadel-machine-key` GSM secret BEFORE Zitadel starts. Document the runbook step in tasks.md §X.

**Why reuse dev pattern**: avoids re-deriving the masterkey-immutability + MachineKey lifecycle invariants. The dev deploy has been stable post-incident-fix; copying its shape minimizes the surface area for new bugs.

**Alternative considered:** prod gets a fresh masterkey + clean Zitadel slate (no migration). That's what we're doing — prod is greenfield. The "reuse dev pattern" refers to the manifest *shape*, not the etcd state.

### D5: PodMonitoring opt-in pattern — per-workload `metricRelabeling` keep-rules

**Decision:** Two PodMonitoring CRDs ship in this change:

1. `k8s/namespaces/backend/overlays/prod/podmonitoring.yaml` — scrapes the backend Connect-RPC server's `/metrics` endpoint. Keep-rules limit ingested series to: `connect_server_*` (Connect-RPC core), `go_goroutines`, `go_memstats_*` (Go runtime), and `process_*` (process-level).
2. `k8s/namespaces/zitadel/overlays/prod/podmonitoring.yaml` — scrapes Zitadel's `/debug/metrics`. Keep-rules limit ingested series to: `zitadel_command_*` (auth command latency / error rate), `http_server_request_duration_*` (auth endpoint latency).

Each PodMonitoring uses `interval: 60s` (4× reduction vs the default 15s) to keep the ingestion rate bounded.

**Why opt-in not blanket:** the `migrate-prod-to-autopilot` spec scenario "GMP managed collection remains enabled" accepts that GKE-managed system scrapes (kubelet, cAdvisor) cannot be turned off. Per-workload PodMonitoring is the *user-controlled* layer — keeping it opt-in (only `backend` + `zitadel` initially) means we never accidentally enable a high-cardinality scrape.

**Alternative considered:** ship PodMonitoring for every workload (frontend, NATS, KEDA, Atlas Operator, etc.). Rejected — most of these don't expose metrics we monitor; auto-scraping them inflates ingestion without operational benefit.

**Future revisit:** when an alert is added that depends on a metric outside the keep-list, the relevant overlay's PodMonitoring keep-rule extends to include it. Adding more workloads to the scraped set is a separate, deliberate decision per workload.

### D6: ArgoCD sync-wave ordering — exact mirror of dev's actual annotations

**Decision:** Each prod Application's `argocd.argoproj.io/sync-wave` annotation matches the dev annotation verbatim. After inspecting `k8s/argocd-apps/dev/*.yaml`, the actual dev pattern is:

| Wave | Applications |
|------|-------------|
| **-1** | `namespaces` |
| **1** | `cluster` |
| **0 (default — no annotation)** | `argocd`, `external-secrets`, `reloader`, `keda`, `nats`, `atlas-operator`, `otel-collector`, `gateway`, `backend-migrations`, `backend`, `frontend`, `zitadel` |

Apps without a `sync-wave` annotation default to wave 0. The `cluster` Application is the one outlier that runs AFTER wave 0 (it depends on CRDs installed by other Apps and seeds cluster-scope resources). The `namespaces` Application runs first (-1) so per-namespace Apps have somewhere to deploy into.

ArgoCD's automatic dependency resolution handles the ordering within wave 0 — resources reference each other (e.g., `backend` Deployments mount Secrets created by ExternalSecret CRs reconciled by `external-secrets`), so the controllers come up before the workloads that depend on them, naturally.

**Why match dev verbatim:** the wave annotations encode the team's tested ordering. Inventing finer-grained waves (e.g., separating `backend-migrations` from `backend`) without empirical evidence of dependency churn is over-engineering — if dev syncs cleanly without those barriers, prod will too.

**Note:** an earlier draft of this design proposed waves 2/3/4 for finer ordering of `nats`/`gateway`, `backend-migrations`, and `backend`/`frontend`/`zitadel`. Verifying against dev showed those waves don't exist in practice. Removed during PR #457 review.

### D7: Lint coverage extension — `lint-k8s` renders both dev and prod overlays

**Decision:** Update `Makefile`'s `lint-k8s` target from:

```makefile
@for overlay in k8s/namespaces/*/overlays/dev; do ...
```

to:

```makefile
@for overlay in k8s/namespaces/*/overlays/{dev,prod}; do ...
```

Both env's overlays render with `kustomize build --enable-helm`, kube-linter runs against the merged output, and `./scripts/check-spot-nodeselector.sh` validates the Spot label on every prod Pod template too.

**Why:** without this, CI on this PR would render only dev — prod overlays could ship broken until first ArgoCD sync surfaces the error. Extending the lint target keeps the safety net.

### D8: Workload scaling — set replicas=1 for all prod Deployments

**Decision:** Prod workload Deployments / StatefulSets default to `replicas: 1`. HPA-driven scaling (via KEDA) can scale up under load, but the baseline is 1 replica per workload to minimize idle node count.

**Why:** with no traffic, replicas=2 means two Pods → Autopilot provisions a second node → 2x the per-node floor cost. Once HPA scaling rules are tuned for prod, replicas can come up. For idle bootstrap, 1 replica per workload is right.

**Trade-off:** loses HA during the bootstrap phase. Acceptable because there are no users to lose during the bootstrap phase.

## Risks / Trade-offs

- **[Risk] First Zitadel sync fails because admin SA key isn't seeded into GSM yet.** → Mitigation: document the GSM-seed step explicitly in tasks.md as a pre-deploy human action; verify via `gcloud secrets versions list zitadel-machine-key --project liverty-music-prod` before triggering ArgoCD sync.
- **[Risk] Gateway sync claims the static IP but DNS still has stale TTL → some users see SERVFAIL.** → Mitigation: not a real risk today (no users), but document that DNS TTL on the existing A records is 300s, so propagation completes within 5 min of sync.
- **[Risk] Backend-migrations Application runs Atlas against an empty prod schema and creates the full schema in one shot.** → This is desired; the prod Cloud SQL `liverty_music` database is empty, and Atlas is the source of truth. The "risk" is incident-finding from migrations that worked on dev's older schema but fail on a fresh-empty schema. → Mitigation: validate the Atlas plan against an empty schema as part of pre-merge lint.
- **[Risk] ExternalSecret reconciliation lag — secret-store auth issues delay all app workloads.** → Mitigation: ArgoCD sync-wave ordering puts `external-secrets` at wave 1, before any workload that depends on it. If ESO's authentication to GSM fails, the failure surfaces at wave 1 (controller crash-loop) before app workloads are even attempted.
- **[Risk] Autopilot machine-type auto-provisioning picks `ek-standard-32` for an unintentional reason and overprovisions.** → Mitigation: each Deployment declares explicit `resources.requests` matching dev's values. Autopilot bin-packs Pods into the smallest fitting machine class. Without huge resource requests, it won't pick large machines.
- **[Trade-off] Single-replica-per-workload during bootstrap means a single Pod crash takes a workload offline.** → Acceptable; no users yet. Re-tune to HA replicas in a follow-up change after first real users.
- **[Trade-off] PodMonitoring is opt-in for only 2 workloads (backend + zitadel) — frontend / NATS / Atlas Operator etc. don't ingest metrics.** → Acceptable; alerts aren't authored for those workloads yet. When alerts arrive, PodMonitoring opts them in per workload.

## Migration Plan

This change is k8s-manifest-only — no Pulumi cluster changes. Deployment is:

1. **Pre-merge prep (human, before opening PR)**:
   - Seed prod ESC values: `esc env set liverty-music/prod pulumiConfig.zitadel.zitadelMachineKey <base64-decoded-admin-key> --secret` and same for `zitadelLoginPat`.
   - (GSM pre-seed deferred to step 5 — the `zitadel-machine-key` Secret resource doesn't exist in prod GSM until Pulumi creates it, so direct `gcloud secrets versions add` here would 404. The pre-seed step has to follow Pulumi creating the Secret.)
2. **PR + CI**:
   - `make lint-k8s` runs against `k8s/namespaces/*/overlays/{dev,prod}` — must pass for all 22 overlays.
   - Pulumi preview runs against prod stack — expect ~6 changes (remove zitadel-prod env-gate from `src/index.ts` flows new ESC values into 2 new prod GSM Secret resources + 2 SecretVersion resources + IAM bindings for those).
3. **Merge**:
   - Merge to main triggers Pulumi auto-deploy on dev (no-op for k8s manifest paths). Prod stays on manual trigger.
4. **Pulumi up for prod (manual, post-merge)**:
   - Trigger `pulumi up --stack prod` from Pulumi Cloud console to apply the Pulumi-side changes (2 new GSM Secrets + IAM bindings). After this step, the `zitadel-machine-key` and `zitadel-login-pat` Secret resources exist in prod GSM with a Pulumi-managed default placeholder version.
5. **GSM pre-seed (human, post-Pulumi-up, pre-ArgoCD-sync)**:
   - Add the prod admin SA key to the now-existing Secret: `gcloud secrets versions add zitadel-machine-key --data-file=/path/to/admin-key.json --project liverty-music-prod`. ESO will read the latest version when Zitadel starts. The bootstrap-uploader sidecar only fires on first-instance Zitadel boot; pre-seeding short-circuits the dependency. Same for `zitadel-login-pat` if needed.
6. **ArgoCD bootstrap (manual, post-pre-seed)**:
   - `kubectl --context gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka apply -k k8s/argocd-apps/prod/` to register the 14 Applications.
   - ArgoCD reconciles wave -1 (`namespaces`) first, then wave 0 default (most Apps including `argocd`, infra controllers, app workloads — ordering resolved by resource dependencies, not by sub-wave annotations), then wave 1 (`cluster`). Total sync time: ~5-15 min.
7. **Verification**:
   - All 14 Applications show Healthy in ArgoCD UI.
   - `api-gateway-static-ip` status: `IN_USE`, claimed by the prod Gateway.
   - `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200 (or appropriate Connect-RPC framing).
   - `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` returns 200 with the Zitadel issuer payload.
   - Autopilot has provisioned ~5-10 nodes hosting the system+infra+app Pods. Spot label honored; all Pods running on Spot-tier compute.

## Open Questions

- **OQ1: Per-workload resource sizing.** Match dev exactly, or pad CPU/memory headroom for prod's expected 2-3x traffic? *Default decision unless raised before implementation:* match dev. Tune in a follow-up `right-size-prod` change once real traffic data exists.
- **OQ2: PodMonitoring `interval` default.** 60s gives 4x reduction vs default 15s but loses some alert responsiveness. Acceptable for the auth + RPC server scenarios planned? *Default decision unless raised:* 60s. Tune per-PodMonitoring if specific alerts need finer resolution.
- **OQ3: Should the `cluster` Application include the cluster-pod-monitoring resource removed during PR #252?** That config was wrong for cost control but might be useful for a different purpose (cluster-scope reference). *Default decision unless raised:* no — PR #252 + PR #253 removed it for good reason; per-workload PodMonitoring (D5) is the right pattern.
- **OQ4: Backend-migrations on a fresh prod schema.** Run Atlas in `--dry-run` first to validate the migration plan? *Default decision unless raised:* yes — add a pre-deploy task to dump the planned migration via `atlas migrate diff --dry-run` against a fresh local Postgres, and review before triggering ArgoCD sync.
