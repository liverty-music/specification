## 1. Pre-flight verification

- [ ] 1.1 Confirm the prod cluster from the just-archived migrate-prod-to-autopilot change is RUNNING and healthy: `gcloud container clusters describe autopilot-cluster-osaka --region asia-northeast2 --project liverty-music-prod --format='value(status,autopilot.enabled)'` returns `RUNNING True`
- [ ] 1.2 Confirm the api-gateway-static-ip is `RESERVED` (unbound) and has the IP `34.110.151.208`: `gcloud compute addresses describe api-gateway-static-ip --global --project liverty-music-prod --format='value(status,address)'`
- [ ] 1.3 Confirm prod Cloud SQL `postgres-osaka` is `RUNNABLE` with the `liverty_music` and `zitadel` databases provisioned (from prior `provision-prod-gcp-resources` work)
- [ ] 1.4 Confirm prod GSM has placeholder Pulumi-managed secrets for the non-Zitadel keys (`lastfm-api-key`, `fanarttv-api-key`, `blockchain-*`, `postgres-admin-password`, `vapid-private-key`, etc.) — these were seeded during the `provision-prod-gcp-resources` archive but verify each has at least one version
- [ ] 1.5 Generate or extract the prod Zitadel admin SA key locally (do NOT add to GSM yet — the `zitadel-machine-key` Secret resource doesn't exist in prod GSM until Pulumi creates it in §9.1; trying to add a version now would 404). Stash the key file safely (e.g., `/tmp/zitadel-admin-key-prod.json`, gitignored) — it gets added to GSM in §9.2 once Pulumi has created the Secret.

## 2. Pulumi-side preparation (`cloud-provisioning/src/`)

- [ ] 2.1 In `src/index.ts` (or wherever the `environment === 'prod'` gate currently lives, around line 73), remove the env-gate that excludes `zitadelMachineKey` and `zitadelLoginPat` ESC reads for prod. After removal, both ESC values flow through to Pulumi for prod, creating 2 new prod GSM Secret resources + IAM bindings (`backend-app` accessor + `eso` accessor).
- [ ] 2.2 Seed the prod ESC env with the Zitadel ESC values. From the prod admin SA key + login PAT:
  - `esc env set liverty-music/prod pulumiConfig.zitadel.zitadelMachineKey <base64-or-json> --secret`
  - `esc env set liverty-music/prod pulumiConfig.zitadel.zitadelLoginPat <pat-string> --secret`
- [ ] 2.3 Run `pulumi preview --stack prod` locally — expect ~6 changes (2 new GSM Secret resources, 2 SecretVersion resources, 2 IAM accessor bindings for backend-app + eso). KMS, cluster, network resources should show no changes.

## 3. ArgoCD Applications (`cloud-provisioning/k8s/argocd-apps/prod/`)

- [ ] 3.1 Create `cloud-provisioning/k8s/argocd-apps/prod/` directory.
- [ ] 3.2 Author 14 Application manifests in `cloud-provisioning/k8s/argocd-apps/prod/`, mirroring `cloud-provisioning/k8s/argocd-apps/dev/` by name: `argocd.yaml`, `atlas-operator.yaml`, `backend-migrations.yaml`, `backend.yaml`, `cluster.yaml`, `external-secrets.yaml`, `frontend.yaml`, `gateway.yaml`, `keda.yaml`, `namespaces.yaml`, `nats.yaml`, `otel-collector.yaml`, `reloader.yaml`, `zitadel.yaml`. For each:
  - Copy the dev version as starting point.
  - Patch `spec.source.path` from `k8s/namespaces/<ns>/overlays/dev` → `k8s/namespaces/<ns>/overlays/prod` (or `k8s/cluster/overlays/prod` for cluster Application).
  - Patch `spec.destination.namespace` if dev hardcodes one (most should already reference the in-overlay namespace).
  - Patch ArgoCD project label if dev uses `argocd-project: dev` → `argocd-project: prod`.
  - Keep `argocd.argoproj.io/sync-wave` annotations identical to dev.
- [ ] 3.3 Verify all 14 Applications point at `*/overlays/prod` (no leftover dev refs): `grep -l "overlays/dev" cloud-provisioning/k8s/argocd-apps/prod/` should return empty.

## 4. Per-namespace prod overlays (`cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/`)

For each of the 10 namespaces missing a prod overlay (`atlas-operator`, `backend`, `external-secrets`, `frontend`, `gateway`, `keda`, `nats`, `otel-collector`, `reloader`, `zitadel`):

- [ ] 4.1 atlas-operator: create overlay with prod-scoped Helm values (target Cloud SQL prod instance, prod IAM SA). Most fields will be the same as dev; the env-divergent piece is the Atlas Operator's per-namespace AtlasMigration CRs that reference the Cloud SQL connection string.
- [ ] 4.2 backend: create overlay with prod hostname (`api.liverty-music.app`), prod ESC-secret refs, prod Connect-RPC server config (allowed-origins includes `https://liverty-music.app`), prod OIDC issuer (`https://auth.liverty-music.app`). Replicas: 1.
- [ ] 4.3 external-secrets: create overlay with prod-scoped `ClusterSecretStore` (gcpsm projectID = `liverty-music-prod`). Includes the patch that the original `argocd/overlays/prod/` ClusterSecretStore patch suggests.
- [ ] 4.4 frontend: create overlay with prod hostname / Aurelia env config (PROJECT_ID = `liverty-music-prod`, OIDC issuer = `https://auth.liverty-music.app`). Replicas: 1.
- [ ] 4.5 gateway: create overlay with prod Gateway CR (`spec.addresses` → `NamedAddress: api-gateway-static-ip`) + prod HTTPRoutes for `api.liverty-music.app` (→ backend) and `auth.liverty-music.app` (→ zitadel-api / zitadel-web path-split per the existing zitadel-self-hosted-deployment spec). Reference the existing Certificate Manager certs via cert-map annotations.
- [ ] 4.6 keda: create overlay with prod Helm values (likely identical to dev; KEDA itself is a controller with no env-divergent state).
- [ ] 4.7 nats: create overlay with prod values for the NATS StatefulSet. Replicas: 1 (per design D8 — dev base has 3 for cluster mode, but prod starts single-replica for cost; cluster-mode is a follow-up change when traffic justifies it). KEDA can scale the StatefulSet later.
- [ ] 4.8 otel-collector: create overlay with prod exporter endpoints (Cloud Trace / Cloud Monitoring SA = prod's `otel-collector` GSA). Resource exporter targets the prod GCP project.
- [ ] 4.9 reloader: create overlay (likely just inherits base; Reloader is a controller with no env-divergent state).
- [ ] 4.10 zitadel: create overlay with prod hostname, prod GSM secret refs, prod Cloud SQL connection, prod OIDC issuer. Match the existing `Per-Environment Overlay Topology` requirement in `zitadel-self-hosted-deployment` spec (must omit the dev-only `zitadel-restart` CronJob). Replicas: 1 for each of `zitadel-api` + `zitadel-web` (per design.md D8).

## 5. Spot label + lint extension

- [ ] 5.1 Run `kubectl kustomize k8s/namespaces/<ns>/overlays/prod` for each of the 11 namespaces — every rendered Pod template MUST have `nodeSelector["cloud.google.com/gke-spot"] = "true"`. Validate the inheritance from base manifests survived all overlay patches.
- [ ] 5.2 Update `cloud-provisioning/Makefile`'s `lint-k8s` target. Change the for-loop from `k8s/namespaces/*/overlays/dev` to `k8s/namespaces/*/overlays/{dev,prod}`. Confirm the rendered output dir naming doesn't collide (e.g., `/tmp/rendered/<ns>.yaml` becomes `/tmp/rendered/<ns>-<env>.yaml`).
- [ ] 5.3 Run `make lint-k8s` — must pass for all 22 overlays (11 namespaces × 2 envs).

## 6. PodMonitoring opt-in CRDs

- [ ] 6.1 Author `cloud-provisioning/k8s/namespaces/backend/overlays/prod/podmonitoring.yaml` — `PodMonitoring` CR scraping the backend Pod's `/metrics` endpoint, with `metricRelabeling` keep-rule regex `connect_server_.+|go_goroutines|go_memstats_.+|process_.+` and `interval: 60s`.
- [ ] 6.2 Author `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/podmonitoring.yaml` — `PodMonitoring` CR scraping the zitadel-api Pod's `/debug/metrics` endpoint, with `metricRelabeling` keep-rule regex `zitadel_command_.+|http_server_request_duration_.+` and `interval: 60s`.
- [ ] 6.3 Add both PodMonitoring files to their respective overlay's `kustomization.yaml` resources list.

## 7. Local validation

- [ ] 7.1 `make lint-ts` in `cloud-provisioning` — must pass after the §2 Pulumi change.
- [ ] 7.2 `make lint-k8s` — must pass with both dev + prod overlays + spot-label check.
- [ ] 7.3 For each prod overlay, run `kustomize build --enable-helm k8s/namespaces/<ns>/overlays/prod | kube-linter lint -` — all 11 overlays must pass kube-linter.
- [ ] 7.4 `kubectl kustomize k8s/argocd-apps/prod` — renders all 14 Applications without error.
- [ ] 7.5 Verify the Backend Atlas migration plan against an empty Postgres: `cd backend; atlas migrate diff --dry-run` against a fresh `postgres:18` Docker container — review output for any DROP TABLE / data-loss patterns that would break a clean-slate prod schema (none expected, but confirm).
- [ ] 7.6 `pulumi preview --stack prod` — confirms only the 6 new GSM-related resources (no cluster churn).

## 8. PR preparation

- [ ] 8.1 Commit changes with Conventional Commits: `feat(infra): bootstrap prod cluster with ArgoCD Applications + per-namespace overlays + Gateway`.
- [ ] 8.2 Open PR in `cloud-provisioning` referencing this OpenSpec change + `migrate-prod-to-autopilot` archive.
- [ ] 8.3 Open companion PR in `specification` with this OpenSpec change (proposal + design + specs/* delta + tasks).
- [ ] 8.4 Wait for Pulumi Cloud auto-preview on both stacks: dev shows zero changes; prod shows the expected 6 GSM-related additions.
- [ ] 8.5 Wait for reviewer approval — given this is the prod-bootstrap PR, require explicit "approved for prod cluster bootstrap" comment before merge.

## 9. Prod cluster bootstrap (manual, after PR merge)

- [ ] 9.1 Trigger `pulumi up --stack prod` from Pulumi Cloud console to apply §2 Pulumi changes (creates the 2 prod GSM Secret resources + 2 Pulumi-managed SecretVersion resources with placeholder values + IAM bindings).
- [ ] 9.2 Pre-seed the prod admin SA key (from §1.5 stash) into the now-existing GSM Secret: `gcloud secrets versions add zitadel-machine-key --data-file=/tmp/zitadel-admin-key-prod.json --project liverty-music-prod`. ESO reads `latest` version by default, so this becomes the active secret for the first Zitadel Pod. Same pattern for `zitadel-login-pat` if a fresh PAT is needed. (The bootstrap-uploader sidecar only fires on first-instance Zitadel boot per memory `reference_zitadel_bootstrap_uploader_scenario_2.md`; pre-seeding short-circuits the dependency.)
- [ ] 9.3 Verify the pre-seeded versions are present: `gcloud secrets versions list zitadel-machine-key --project liverty-music-prod` returns ≥2 versions (the Pulumi-managed placeholder from §9.1 + the §9.2 admin-key version, with the admin-key version being `latest`).
- [ ] 9.4 Apply the prod ArgoCD Applications: `kubectl --context gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka apply -k k8s/argocd-apps/prod/` (or via the bootstrap script if one exists). This registers all 14 Applications with the in-cluster ArgoCD.
- [ ] 9.5 Watch ArgoCD reconcile (per design D6 — dev's actual 3-wave pattern):
  - Wave **-1**: `namespaces` Application creates 11 namespaces.
  - Wave **0** (default — no annotation): most Apps in parallel, including `argocd` (self-management), `external-secrets`, `reloader`, `keda`, `nats`, `atlas-operator`, `otel-collector`, `gateway`, `backend-migrations`, `backend`, `frontend`, `zitadel`. ArgoCD's dependency resolution handles ordering inside the wave (controllers come up before workloads that depend on their CRDs/Services).
  - Wave **1**: `cluster` Application runs last (depends on CRDs installed by other Apps).
- [ ] 9.6 Monitor Autopilot node provisioning during the sync — Pods that need nodes trigger Autopilot to provision them; expect ~5-10 nodes by sync completion.

## 10. Post-bootstrap verification

- [ ] 10.1 Verify all 14 Applications are Healthy in ArgoCD: `kubectl --context <prod> get applications -n argocd -o json | jq -r '.items[] | "\(.metadata.name): \(.status.health.status) / \(.status.sync.status)"'` — every row should show `Healthy / Synced`.
- [ ] 10.2 Verify the static IP is now `IN_USE`: `gcloud compute addresses describe api-gateway-static-ip --global --project liverty-music-prod --format='value(status,users[])'` returns `IN_USE` plus a Gateway target.
- [ ] 10.3 Verify api.liverty-music.app responds: `curl -I https://api.liverty-music.app/grpc.health.v1.Health/Check` returns 200 (or Connect-RPC valid framing). Per memory `reference_liverty_dev_endpoints.md`, the auth-exempt `grpc.health.v1.Health/Check` is the appropriate smoke endpoint.
- [ ] 10.4 Verify auth.liverty-music.app serves the Zitadel issuer: `curl -s https://auth.liverty-music.app/.well-known/openid-configuration | jq -r '.issuer'` returns `https://auth.liverty-music.app`.
- [ ] 10.5 Verify the GMP PodMonitoring CRDs are active: `kubectl get podmonitoring -n backend && kubectl get podmonitoring -n zitadel` — both show the opted-in scrape configs.
- [ ] 10.6 Wait 30 minutes for first GMP scrape cycle. Check Cloud Monitoring Metrics Management page — only `backend` + `zitadel` workload metrics SHALL appear (no auto-discovery of other workloads).
- [ ] 10.7 Verify Spot Pod billing: `gcloud container clusters describe autopilot-cluster-osaka --region asia-northeast2 --project liverty-music-prod` + check the node pool list — every node SHALL be in a Spot-class pool. Pods with the `cloud.google.com/gke-spot: "true"` label are billed at Spot Pod rates.

## 11. Archive

- [ ] 11.1 Update spec.md / design.md / tasks.md with any incident notes from the live bootstrap (Zitadel-bootstrap-uploader-sidecar status, actual sync duration, any wave-stalls, observed GMP ingestion volume).
- [ ] 11.2 Run `openspec validate prod-k8s-manifests --strict` — must pass.
- [ ] 11.3 Sync delta specs to main specs (`openspec/specs/prod-environment-bootstrap/spec.md`, `openspec/specs/zitadel-self-hosted-deployment/spec.md`) and add the new `openspec/specs/prod-k8s-manifests/spec.md` — apply MODIFIED/ADDED/REMOVED operations.
- [ ] 11.4 Move change directory: `git mv openspec/changes/prod-k8s-manifests openspec/changes/archive/YYYY-MM-DD-prod-k8s-manifests`.
- [ ] 11.5 `git add` modifications + main spec changes, commit with `chore(openspec): archive prod-k8s-manifests`, push and merge the archive PR.
