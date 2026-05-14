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
- `ZITADEL_DATABASE_POSTGRES_USER_USERNAME` → `zitadel@liverty-music-prod.iam` SQL user
- Mounted secret (Zitadel Pod only): `zitadel-masterkey` from `liverty-music-prod` GSM, via ExternalSecret pointing at the prod-scoped ClusterSecretStore. The `zitadel-machine-key-for-pulumi-admin` secret is NOT mounted into the Zitadel Pod — that key is an org-admin machine-user JWT consumed by Pulumi (stack applies that act as the Zitadel org-admin) and optionally by the backend (via the separate `zitadel-machine-key-for-backend-app` mechanism). Mounting it into the Zitadel runtime Pod would widen the blast radius unnecessarily.
- `ZITADEL_API_URL` → `https://auth.liverty-music.app`
- `ZITADEL_EXTERNALDOMAIN` → `auth.liverty-music.app`

**Pulumi-side change:** lift the `env === 'dev'` gate at `src/index.ts:119` so prod also instantiates `SecretsComponent('zitadel-secrets', ...)`. That component (`src/zitadel/components/secrets.ts`) creates:

1. `zitadel-masterkey` GSM Secret with a Pulumi-generated 32-char random value (first version).
2. `zitadel-machine-key-for-pulumi-admin` GSM Secret as an **empty shell** (no initial version — populated on first Zitadel boot, see "Bootstrap flow" below).
3. ESO accessor IAM bindings on both Secrets.
4. Zitadel SA `secretVersionAdder` role on `zitadel-machine-key-for-pulumi-admin` so the bootstrap-uploader sidecar can write to it.

The `zitadelMachineKey` / `zitadelLoginPat` Pulumi `Output`s at `src/index.ts:72-95` are NOT what gets gated — those are SaaS Zitadel Cloud-tenant integration outputs and remain dev-only (prod uses in-cluster Zitadel exclusively).

**Bootstrap flow** (per the canonical `zitadel-self-hosted-deployment` "Bootstrap Admin Machine Key Stored in Secret Manager" requirement):

1. Pulumi `pulumi up --stack prod` creates the masterkey (with value) + admin-machine-key (empty shell).
2. ArgoCD syncs the Zitadel workload. First-time Zitadel API container boots against the empty `zitadel` database with `ZITADEL_FIRSTINSTANCE_*` env vars set.
3. Zitadel generates an initial admin machine user and writes the JWT-profile JSON key to a shared `emptyDir` volume.
4. The `bootstrap-uploader` sidecar container co-located in the same Pod reads the file from `emptyDir`, uploads it to `zitadel-machine-key-for-pulumi-admin` via `gcloud secrets versions add` (Pod identity has `secretVersionAdder` role per the IAM binding above), and `unlink`s the file from the shared volume so the org-admin private key doesn't persist.
5. ESO reads the now-populated `zitadel-machine-key-for-pulumi-admin` GSM Secret and mounts it into the backend Pod for runtime use (NOT the Zitadel Pod — see the "Mounted secret" bullet above for the blast-radius rationale).

**No human pre-seed step is required.** Earlier drafts of this design proposed a manual `gcloud secrets versions add` before the first sync — that's redundant because the bootstrap-uploader sidecar performs the seed automatically on first boot. Memory `reference_zitadel_bootstrap_uploader_scenario_2.md` notes that the sidecar only fires on first-instance bootstrap (subsequent boots idle); for greenfield prod, the first boot IS the first-instance bootstrap, so the sidecar fires normally.

**Why reuse dev pattern**: avoids re-deriving the masterkey-immutability + MachineKey lifecycle invariants. The dev deploy has been stable post-incident-fix; copying its shape minimizes the surface area for new bugs.

**Alternative considered:** prod gets a fresh masterkey + clean Zitadel slate (no migration). That's what we're doing — prod is greenfield. The "reuse dev pattern" refers to the manifest *shape* and the bootstrap mechanism, not the etcd state.

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

to (explicit listing, not brace expansion — Make's default `SHELL=/bin/sh` is `dash` on Debian-family runners, which does not expand `{dev,prod}`; the literal token would iterate once over a non-existent path and silently lint nothing):

```makefile
@for overlay in k8s/namespaces/*/overlays/dev k8s/namespaces/*/overlays/prod k8s/cluster/overlays/dev k8s/cluster/overlays/prod; do ...
```

All env+scope overlays render with `kustomize build --enable-helm`, kube-linter runs against the merged output, and `./scripts/check-spot-nodeselector.sh` validates the Spot label on every prod Pod template too. The cluster overlays (`k8s/cluster/overlays/{dev,prod}` — see tasks.md §4.11 for prod authoring) are included so the `cluster` Application's source path is also linted.

**Why:** without this, CI on this PR would render only dev — prod overlays could ship broken until first ArgoCD sync surfaces the error. Extending the lint target keeps the safety net.

### D8: Workload scaling — set replicas=1 for all prod Deployments

**Decision:** Prod workload Deployments / StatefulSets default to `replicas: 1`. HPA-driven scaling (via KEDA) can scale up under load, but the baseline is 1 replica per workload to minimize idle node count.

**Why:** with no traffic, replicas=2 means two Pods → Autopilot provisions a second node → 2x the per-node floor cost. Once HPA scaling rules are tuned for prod, replicas can come up. For idle bootstrap, 1 replica per workload is right.

**Trade-off:** loses HA during the bootstrap phase. Acceptable because there are no users to lose during the bootstrap phase.

## Risks / Trade-offs

- **[Risk] First Zitadel sync fails because the bootstrap-uploader sidecar can't write to `zitadel-machine-key-for-pulumi-admin` (e.g., empty shell wasn't created or IAM binding is missing).** → Mitigation: pre-deploy verification (tasks.md §9.2) confirms `pulumi up --stack prod` has created the empty shell + the `secretVersionAdder` IAM binding on the Zitadel SA before triggering ArgoCD sync. If the shell is missing, the sidecar's `gcloud secrets versions add` call would 404, surfaced as a sidecar-container crash-loop visible in the Zitadel Pod status (caught before the Zitadel API container becomes Ready).
- **[Risk] Gateway sync claims the static IP but DNS still has stale TTL → some users see SERVFAIL.** → Mitigation: not a real risk today (no users), but document that DNS TTL on the existing A records is 300s, so propagation completes within 5 min of sync.
- **[Risk] Backend-migrations Application runs Atlas against an empty prod schema and creates the full schema in one shot.** → This is desired; the prod Cloud SQL `liverty_music` database is empty, and Atlas is the source of truth. The "risk" is incident-finding from migrations that worked on dev's older schema but fail on a fresh-empty schema. → Mitigation: validate the Atlas plan against an empty schema as part of pre-merge lint.
- **[Risk] ExternalSecret reconciliation lag — secret-store auth issues delay all app workloads.** → Mitigation: ArgoCD's intra-wave dependency resolution handles the ordering at wave 0 — application Pods that reference ExternalSecret-managed Kubernetes Secrets stay `Pending`/`ContainerCreating` until ESO has reconciled the CRs successfully. An ESO auth failure surfaces as a CRD reconcile error (visible in the `external-secrets` Application's status in ArgoCD) before any dependent Pod becomes Ready, so it's caught early without needing a barrier wave.
- **[Risk] Autopilot machine-type auto-provisioning picks `e2-standard-32` (or similarly oversized class) for an unintentional reason and overprovisions.** → Mitigation: each Deployment declares explicit `resources.requests` matching dev's values. Autopilot bin-packs Pods into the smallest fitting machine class. Without huge resource requests, it won't pick large machines.
- **[Trade-off] Single-replica-per-workload during bootstrap means a single Pod crash takes a workload offline.** → Acceptable; no users yet. Re-tune to HA replicas in a follow-up change after first real users.
- **[Trade-off] PodMonitoring is opt-in for only 2 workloads (backend + zitadel) — frontend / NATS / Atlas Operator etc. don't ingest metrics.** → Acceptable; alerts aren't authored for those workloads yet. When alerts arrive, PodMonitoring opts them in per workload.

## Migration Plan

This change is k8s-manifest-only — no Pulumi cluster changes. Deployment is:

1. **Pre-merge prep (human, before opening PR)**:
   - No prod ESC seeding required for Zitadel — the masterkey is Pulumi-generated (random 32-char string by `SecretsComponent`), and the admin machine key is populated automatically by the in-cluster `bootstrap-uploader` sidecar on first Zitadel boot (per D4 + the canonical `zitadel-self-hosted-deployment` bootstrap requirement).
2. **PR + CI**:
   - `make lint-k8s` runs against `k8s/namespaces/*/overlays/dev`, `k8s/namespaces/*/overlays/prod`, `k8s/cluster/overlays/dev`, `k8s/cluster/overlays/prod` (explicit listing — see D7 for the sh-compat reason) — must pass for all 24 overlays (11 namespaces × 2 envs + 1 cluster × 2 envs).
   - Pulumi preview runs against prod stack — expect ~6 changes from lifting the `env === 'dev'` gate at `src/index.ts:119`: 2 new prod GSM Secret resources (`zitadel-masterkey`, `zitadel-machine-key-for-pulumi-admin`) + 1 SecretVersion (the masterkey value — admin-machine-key stays an empty shell) + 3 IAM bindings (ESO read on both Secrets, Zitadel SA `secretVersionAdder` on admin-machine-key).
3. **Merge**:
   - Merge to main triggers Pulumi auto-deploy on dev (no-op for k8s manifest paths). Prod stays on manual trigger.
4. **Pulumi up for prod (manual, post-merge)**:
   - Trigger `pulumi up --stack prod` from Pulumi Cloud console to apply the Pulumi-side changes (2 new GSM Secrets + IAM bindings). After this step, `zitadel-masterkey` has a value and `zitadel-machine-key-for-pulumi-admin` is an empty shell.
5. **ArgoCD bootstrap (manual, post-Pulumi-up)**:
   - `kubectl --context gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka apply -k k8s/argocd-apps/prod/` to register the 14 Applications.
   - ArgoCD reconciles wave -1 (`namespaces`) first, then wave 0 default (most Apps including `argocd`, infra controllers, app workloads — ordering resolved by resource dependencies, not by sub-wave annotations), then wave 1 (`cluster`). Total sync time: ~5-15 min.
   - During the wave 0 sync, the first-time Zitadel API container boot triggers the bootstrap-uploader sidecar to populate `zitadel-machine-key-for-pulumi-admin` with the generated admin JWT-profile key. ESO then mounts it into the backend Pod for runtime use.
6. **Verification**:
   - All 14 Applications show Healthy in ArgoCD UI.
   - `api-gateway-static-ip` status: `IN_USE`, claimed by the prod Gateway.
   - `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200 (or appropriate Connect-RPC framing).
   - `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` returns 200 with the Zitadel issuer payload.
   - Autopilot has provisioned ~5-10 nodes hosting the system+infra+app Pods. Spot label honored; all Pods running on Spot-tier compute.

## Open Questions

- **OQ1: Per-workload resource sizing.** Match dev exactly, or pad CPU/memory headroom for prod's expected 2-3x traffic? *Default decision unless raised before implementation:* match dev. Tune in a follow-up `right-size-prod` change once real traffic data exists.
- **OQ2: PodMonitoring `interval` default.** 60s gives 4x reduction vs default 15s but loses some alert responsiveness. Acceptable for the auth + RPC server scenarios planned? *Default decision unless raised:* 60s. Tune per-PodMonitoring if specific alerts need finer resolution.
- **OQ3: Should the `cluster` Application include the cluster-pod-monitoring resource removed during PR #252?** That config was wrong for cost control but might be useful for a different purpose (cluster-scope reference). *Default decision unless raised:* no — PR #252 + PR #253 removed it for good reason; per-workload PodMonitoring (D5) is the right pattern.
- **OQ4: Backend-migrations on a fresh prod schema.** Run Atlas in `--dry-run` first to validate the migration plan? *Default decision unless raised:* yes — add a pre-deploy task to replay the existing migration files via `atlas migrate apply --dry-run` against a fresh local Postgres, and review the output for DROP TABLE / data-loss patterns before triggering ArgoCD sync. (Note: `migrate apply --dry-run` replays the migration directory, which is the right command for this goal; `migrate diff --dry-run` would generate a NEW migration by diffing the desired schema against the directory — wrong tool.)
