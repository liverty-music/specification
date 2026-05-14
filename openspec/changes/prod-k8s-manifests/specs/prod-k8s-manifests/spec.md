## ADDED Requirements

### Requirement: Prod cluster SHALL run a full ArgoCD Application set matching dev's structure
The `cloud-provisioning/k8s/argocd-apps/prod/` directory SHALL contain ArgoCD `Application` manifests covering the same 14 deployment units the dev environment ships: `argocd`, `atlas-operator`, `backend-migrations`, `backend`, `cluster`, `external-secrets`, `frontend`, `gateway`, `keda`, `namespaces`, `nats`, `otel-collector`, `reloader`, `zitadel`. Each Application SHALL point its `spec.source.path` at the corresponding `k8s/namespaces/<ns>/overlays/prod/` (or `k8s/cluster/overlays/prod/` for cluster-scope). Sync-wave annotations SHALL match dev's wave assignments so dependency ordering (CRDs → controllers → workloads) is preserved.

#### Scenario: All 14 prod Applications exist
- **WHEN** listing files in `cloud-provisioning/k8s/argocd-apps/prod/`
- **THEN** the directory SHALL contain exactly 14 `.yaml` files matching the dev set by name: `argocd.yaml`, `atlas-operator.yaml`, `backend-migrations.yaml`, `backend.yaml`, `cluster.yaml`, `external-secrets.yaml`, `frontend.yaml`, `gateway.yaml`, `keda.yaml`, `namespaces.yaml`, `nats.yaml`, `otel-collector.yaml`, `reloader.yaml`, `zitadel.yaml`

#### Scenario: Each Application points at the prod overlay
- **WHEN** reading any prod Application's `spec.source.path`
- **THEN** the path SHALL end in `/overlays/prod` (not `/overlays/dev`)

#### Scenario: Sync-wave ordering matches dev
- **WHEN** comparing `argocd.argoproj.io/sync-wave` annotations across the 14 prod Applications
- **THEN** each wave SHALL equal the corresponding dev Application's wave (so the cross-wave dependency graph is identical)

### Requirement: Every prod namespace under `k8s/namespaces/` SHALL have a `prod/` overlay
For each of the 11 namespaces under `cloud-provisioning/k8s/namespaces/` (`argocd`, `atlas-operator`, `backend`, `external-secrets`, `frontend`, `gateway`, `keda`, `nats`, `otel-collector`, `reloader`, `zitadel`), an `overlays/prod/` subdirectory SHALL exist with a valid `kustomization.yaml`. Each overlay SHALL render successfully via `kubectl kustomize` (or `kustomize build --enable-helm` for Helm-based overlays).

#### Scenario: 11 prod overlays exist
- **WHEN** running `find k8s/namespaces -maxdepth 3 -type d -name prod`
- **THEN** the output SHALL list 11 directories, one per namespace

#### Scenario: Every prod overlay renders
- **WHEN** running `kustomize build --enable-helm k8s/namespaces/<ns>/overlays/prod` for each of the 11 namespaces
- **THEN** the command SHALL exit with code 0 and emit valid YAML

### Requirement: Prod overlays SHALL diverge from dev only by ESC secret refs, hostnames, ArgoCD project labels, replica counts, and (when needed) resource requests/limits
Each prod overlay's kustomize patches SHALL be limited to the *minimal* set of env-divergent fields:
1. `ExternalSecret.spec.secretStoreRef.name` patched to a prod-scoped SecretStore (e.g., `google-secret-manager-prod`)
2. Hostnames in ConfigMap data and HTTPRoute `spec.hostnames`: `api.dev.liverty-music.app` → `api.liverty-music.app`, `auth.dev.liverty-music.app` → `auth.liverty-music.app`
3. ArgoCD project labels or Application metadata as needed
4. Resource requests/limits SHALL match dev's values (no env-specific sizing yet)

Image references SHALL NOT be patched per env — both envs use the same images with ArgoCD Image Updater managing tag bumps. Replica counts SHALL be `1` for all workload `Deployment` AND `StatefulSet` resources in prod (HPA / KEDA-driven scale-up is the path to multi-replica).

#### Scenario: No image-tag divergence between dev and prod overlays
- **WHEN** diffing the rendered output of `k8s/namespaces/backend/overlays/dev` and `k8s/namespaces/backend/overlays/prod` (and similarly for other namespaces)
- **THEN** container image references SHALL be identical (tags + digests match)
- **AND** the only differences SHALL be: hostnames, secret references, project labels, resource requests/limits (when env-divergent), and replica counts (per design D8)

#### Scenario: Single replica per Deployment and StatefulSet for prod
- **WHEN** rendering any prod overlay
- **THEN** every `Deployment` SHALL have `spec.replicas: 1`
- **AND** every `StatefulSet` SHALL have `spec.replicas: 1`
- **AND** HPA / KEDA `ScaledObject` resources MAY exist to scale beyond 1 under load (not in scope for this change to author the autoscalers themselves)

### Requirement: Every Pod template in prod overlays SHALL include the gke-spot nodeSelector
Every Pod template (Deployment, StatefulSet, DaemonSet, Job, CronJob) rendered from any `k8s/namespaces/<ns>/overlays/prod/` SHALL include `spec.template.spec.nodeSelector["cloud.google.com/gke-spot"] = "true"`. Workloads inherit this from the base manifests (which already enforce it for dev); the prod lint SHALL verify the inheritance survived the overlay patches.

The repo's `Makefile` `lint-k8s` target SHALL render *both* dev and prod overlays and run `./scripts/check-spot-nodeselector.sh` against both rendered outputs.

#### Scenario: lint-k8s covers prod overlays
- **WHEN** running `make lint-k8s`
- **THEN** the target SHALL render every overlay under `k8s/namespaces/*/overlays/{dev,prod}` (not just `dev`)
- **AND** `./scripts/check-spot-nodeselector.sh` SHALL run against the prod rendered output
- **AND** the lint SHALL pass iff every Pod template in both envs has the gke-spot nodeSelector

#### Scenario: Spot label present on every prod Pod
- **WHEN** rendering any `k8s/namespaces/<ns>/overlays/prod/` and extracting Pod templates
- **THEN** every Pod template SHALL have `nodeSelector["cloud.google.com/gke-spot"] = "true"`

### Requirement: Prod Gateway SHALL bind to the existing api-gateway-static-ip and serve api./auth. hostnames
The prod Gateway CR in `k8s/namespaces/gateway/overlays/prod/` SHALL declare `spec.addresses` referencing the existing `api-gateway-static-ip` global address (provisioned by Pulumi, current value `34.110.151.208`, currently `RESERVED`/unbound). HTTPRoutes SHALL attach to this Gateway with `hostnames: [api.liverty-music.app]` and `hostnames: [auth.liverty-music.app]` respectively, routing to the `backend` Service in the `backend` namespace and the `zitadel` Service in the `zitadel` namespace.

After ArgoCD sync, the static IP SHALL transition from `RESERVED` to `IN_USE`, claimed by the prod Gateway. The pre-existing Cloud DNS A records SHALL begin resolving to a live HTTPS listener without any DNS change.

#### Scenario: Gateway references the named static IP
- **WHEN** reading the rendered Gateway CR from `k8s/namespaces/gateway/overlays/prod/`
- **THEN** `spec.addresses[*].value` SHALL include `api-gateway-static-ip`
- **AND** `spec.addresses[*].type` SHALL be `NamedAddress`

#### Scenario: HTTPRoutes target prod hostnames
- **WHEN** listing HTTPRoute resources in the rendered prod gateway overlay
- **THEN** at least one HTTPRoute SHALL have `hostnames` including `api.liverty-music.app` and `backendRefs` pointing at the `backend` Service in namespace `backend`
- **AND** at least one HTTPRoute SHALL have `hostnames` including `auth.liverty-music.app` with path-split `backendRefs` per the canonical `zitadel-self-hosted-deployment` Two-Container Deployment requirement: path prefix `/ui/v2/login` → `zitadel-web` Service (port 3000), all other paths → `zitadel-api` Service (port 8080), both in namespace `zitadel`

#### Scenario: Static IP becomes IN_USE after sync
- **WHEN** querying `gcloud compute addresses describe api-gateway-static-ip --global --project liverty-music-prod` after the gateway Application has synced Healthy
- **THEN** `status` SHALL equal `IN_USE`
- **AND** the address value SHALL still equal `34.110.151.208` (no IP change)

### Requirement: Prod cluster SHALL opt application workloads into GMP via per-workload PodMonitoring CRDs
Application metric ingestion into Google Managed Service for Prometheus SHALL be opt-in per workload via `PodMonitoring` (or `ClusterPodMonitoring`) CRDs authored in the namespace overlays. Each opt-in CR SHALL include `metricRelabeling` `keep`-rules limiting ingested series to an explicit allow-list that matches what the workload's active alerts consume. Scrape `interval` SHALL be `60s` (or longer) for every endpoint.

Initial opt-in set:
- `k8s/namespaces/backend/overlays/prod/podmonitoring.yaml`: scrapes the backend Pod's `/metrics`, keep-list `connect_server_*`, `go_goroutines`, `go_memstats_*`, `process_*`.
- `k8s/namespaces/zitadel/overlays/prod/podmonitoring.yaml`: scrapes the zitadel Pod's `/debug/metrics`, keep-list `zitadel_command_*`, `http_server_request_duration_*`.

No other workload SHALL be opted in until a metric-based alert demands it.

#### Scenario: PodMonitoring opt-in count matches the alert-driven workload set
- **WHEN** running `kubectl get podmonitoring,clusterpodmonitoring -A` on the prod cluster (excluding addon-managed CRs in `gke-managed-cim` and `gke-gmp-system`)
- **THEN** at most 2 PodMonitoring resources SHALL exist (one in `backend`, one in `zitadel`)
- **AND** each SHALL have `metricRelabeling` with a `keep`-action rule
- **AND** each SHALL have `spec.endpoints[*].interval == 60s`

#### Scenario: Backend PodMonitoring scope is bounded
- **WHEN** reading the backend PodMonitoring's `metricRelabeling`
- **THEN** the `keep`-rule regex SHALL be `connect_server_.+|go_goroutines|go_memstats_.+|process_.+`

#### Scenario: Zitadel PodMonitoring scope is bounded
- **WHEN** reading the zitadel PodMonitoring's `metricRelabeling`
- **THEN** the `keep`-rule regex SHALL be `zitadel_command_.+|http_server_request_duration_.+`
