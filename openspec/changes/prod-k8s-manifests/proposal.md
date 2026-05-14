## Why

The just-merged `migrate-prod-to-autopilot` left the prod cluster fully bootstrapped on the GCP side (Autopilot regional cluster, KMS, Cloud SQL, Cloud DNS, Certificate Manager, Service Accounts, Secret Manager) but **deliberately scoped k8s manifests out** — there is no `argocd-apps/prod/` directory and only one namespace has a `prod/` overlay (`argocd` itself). The cluster is therefore alive but idle: Autopilot has provisioned zero nodes and no workload-side traffic flows.

This change closes the loop. After it lands, prod runs the same 14 ArgoCD Applications as dev, the api-gateway-static-ip (currently `RESERVED`, unbound) gets bound to a prod Gateway, the existing `api.liverty-music.app` + `auth.liverty-music.app` Cloud DNS A records resolve to live HTTPRoutes, and self-hosted Zitadel becomes available as the prod OIDC issuer at `auth.liverty-music.app`. Once verified, the dev cluster can be retired, transferring the full `$74.40/mo` GKE free-tier credit onto prod (the $50-70/mo savings the migrate change unlocked).

## What Changes

- **NEW**: `k8s/argocd-apps/prod/` directory with 14 ArgoCD `Application` manifests mirroring `argocd-apps/dev/` (`argocd`, `atlas-operator`, `backend-migrations`, `backend`, `cluster`, `external-secrets`, `frontend`, `gateway`, `keda`, `namespaces`, `nats`, `otel-collector`, `reloader`, `zitadel`).
- **NEW**: 10 per-namespace `prod/` overlays under `k8s/namespaces/<ns>/overlays/prod/` (every existing namespace except `argocd`, which already has a prod overlay) — each with prod-specific patches for ConfigMap values, ExternalSecret references (pointing at `liverty-music/prod` ESC secrets), hostnames, and resource limits.
- **NEW**: `k8s/namespaces/gateway/overlays/prod/` — Gateway + HTTPRoutes pointing at `api.liverty-music.app` (backend) and `auth.liverty-music.app` (Zitadel), with the Gateway's `addresses` field binding to the existing `api-gateway-static-ip` (34.110.151.208). On ArgoCD sync, the prod Gateway claims the static IP without DNS changes (records already point at it).
- **NEW**: `k8s/namespaces/zitadel/overlays/prod/` — self-hosted Zitadel for prod with the same masterkey immutability + MachineKey lifecycle pattern as dev, scoped to the prod GSM secrets (`zitadel-masterkey`, `zitadel-machine-key-for-pulumi-admin` in `liverty-music-prod`) and the prod Cloud SQL `zitadel` database. Removes the implicit env-gate at `src/index.ts:119` so prod also instantiates `SecretsComponent('zitadel-secrets', ...)`.
- **NEW**: Per-namespace `PodMonitoring` CRDs (opt-in) for workloads that emit metrics the team actively monitors — initially just `backend` (Connect-RPC server metrics, ZeroEx instrumentation) and `zitadel` (auth latency / error rate). Authored as part of the namespace overlay, with `metricRelabeling` keep-rules limiting each workload's series to what its alerts consume. Honors the prod cluster's `autoMonitoringConfig.scope: NONE` (default) by making metric ingestion explicit per workload.
- **NEW**: Spot label enforcement in lint — every Pod template in prod overlays SHALL include `cloud.google.com/gke-spot: "true"` nodeSelector. The `Makefile`'s `lint-k8s` target is extended to render prod overlays (currently only renders dev) and run `./scripts/check-spot-nodeselector.sh` against them.
- **BREAKING (operational, not API)**: the static IP `api-gateway-static-ip` will transition from `RESERVED` (unbound) to `IN_USE` once the Gateway syncs. Brief window during the first ArgoCD sync where the IP exists but no Gateway is claiming it — same window as a normal Gateway creation. Acceptable since no live users yet.

## Capabilities

### New Capabilities

- `prod-k8s-manifests`: contracts the prod Kubernetes manifest set — per-namespace overlay existence + shape, hostname mapping, ESC secret sourcing, Gateway binding to the static IP, Spot label enforcement, PodMonitoring opt-in pattern, ArgoCD Application set. Per-workload runtime/network requirements stay in their respective specs (e.g., `zitadel-self-hosted-deployment`, `gke-gateway-infrastructure`); this spec is about the *prod manifest set* as a coherent unit.

### Modified Capabilities

- `prod-environment-bootstrap`: remove the existing "Prod GCP infrastructure ships without ArgoCD bootstrap (workloads in follow-up change)" requirement. After this change, prod ships *with* the full manifest set. The companion "follow-up change is tracked separately" scenario is also removed.
- `zitadel-self-hosted-deployment`: extend the existing dev-scoped *runtime* requirement (cluster + OIDC issuer URL) to apply equally to prod. The other dev-scoped requirements in that capability (Cloud SQL Connection via Auth Proxy Sidecar, Database & IAM User pre-provisioning, Bootstrap Admin Machine Key Storage) describe env-specific values (`liverty-music-dev:asia-northeast2:postgres-osaka`, etc.) that the prod overlay-level patches replicate for prod via env-divergent kustomize fields — runtime behavior is correct for both envs after this change. A separate consolidation change can broaden those dev-scoped specs to be env-agnostic; that doc cleanup is intentionally out of scope here to avoid PR-scope creep.

## Impact

- **`cloud-provisioning/k8s/argocd-apps/prod/`** (NEW): 14 Application yamls
- **`cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/`** (NEW × 10): one per namespace except already-existing `argocd`
- **`cloud-provisioning/k8s/namespaces/backend/overlays/prod/`** (NEW): PodMonitoring CRD for opt-in app metrics
- **`cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/`** (NEW): PodMonitoring + Zitadel workload manifests
- **`cloud-provisioning/Makefile`**: `lint-k8s` extended to render both `dev` and `prod` overlays
- **`cloud-provisioning/src/index.ts`**: lift the `env === 'dev'` gate at line ~119 around `SecretsComponent('zitadel-secrets', ...)` so prod also instantiates the component. The component (`src/zitadel/components/secrets.ts`) creates `zitadel-masterkey` (with a Pulumi-generated random value) and `zitadel-machine-key-for-pulumi-admin` (empty shell) GSM Secrets + IAM bindings. The separate `zitadelMachineKey`/`zitadelLoginPat` Outputs from the SaaS `Zitadel` class at lines ~72-95 remain dev-only — prod uses in-cluster Zitadel exclusively.
- **Prod GSM secrets**: no human pre-seed required. `zitadel-masterkey` is Pulumi-generated; `zitadel-machine-key-for-pulumi-admin` is populated automatically by the in-cluster `bootstrap-uploader` sidecar on first Zitadel API Pod boot, per the canonical `zitadel-self-hosted-deployment` bootstrap mechanism.
- **Risk**: large manifest churn; bounded by ArgoCD's sync-wave ordering (`namespaces` first at wave -1, then most Apps including `argocd`/infra/workloads together at default wave 0 with intra-wave dependency resolution, then `cluster` last at wave 1) and the fact that prod is currently empty — no in-flight workloads to disrupt.
- **Cost impact**: workloads landing → Autopilot provisions nodes → first real per-Pod billing begins. Spot label keeps the discount tier. GMP cost stays at the autoMonitoringConfig=NONE floor + opt-in PodMonitoring volume from `backend` and `zitadel`. Empirical band: ~$5-15/mo GMP + ~$5-15/mo Compute per workload set, well inside the migrate change's savings envelope.
- **Out of scope**: dev cluster retirement (a separate operational decision); blockchain workload manifests (deferred to `prod-blockchain-workloads` if/when the testnet → mainnet phase arrives); per-region multi-cluster setup.
