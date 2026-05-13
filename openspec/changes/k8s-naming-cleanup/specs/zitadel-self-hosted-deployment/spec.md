## MODIFIED Requirements

### Requirement: Two-Container Deployment with Path-Based Routing

The system SHALL deploy Zitadel as two separate Kubernetes Deployments — one for the API container (`ghcr.io/zitadel/zitadel`, port `8080`, Deployment name `zitadel-api`, container name `api`) and one for the Login V2 UI container (`ghcr.io/zitadel/zitadel-login`, port `3000`, Deployment name `zitadel-web`, container name `web`) — and SHALL expose both through a single hostname via a GKE Gateway `HTTPRoute` that routes the path prefix `/ui/v2/login` to the Web Service (`zitadel-web`) and all other paths to the API Service (`zitadel-api`).

**Rationale**: Zitadel v4 split the Login UI into a dedicated container. Keeping both on the same hostname preserves OIDC issuer identity; path-based routing avoids the extra DNS and certificate surface of a second hostname. Resource names follow the platform-wide `<role>-<tier>` convention (`zitadel-api`, `zitadel-web`) so operator tooling (`kubectl get -n zitadel`, in-cluster DNS) is unambiguous; container names are the short forms (`api`, `web`) for log readability. The image path is `ghcr.io/zitadel/zitadel-login`, NOT `ghcr.io/zitadel/login` (the latter 404s); the upstream Helm chart default uses the same path.

#### Scenario: API request reaches the API container

- **WHEN** a request arrives at `https://auth.dev.liverty-music.app/oauth/v2/keys`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-api` Service on port `8080`

#### Scenario: Login UI request reaches the Web container

- **WHEN** a browser requests `https://auth.dev.liverty-music.app/ui/v2/login/register`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-web` Service on port `3000`

#### Scenario: HealthCheckPolicy targets the renamed Services

- **WHEN** the GKE Gateway evaluates backend health
- **THEN** a `HealthCheckPolicy` named `zitadel-api-policy` SHALL target the `zitadel-api` Service with probe path `/debug/healthz`
- **AND** a `HealthCheckPolicy` named `zitadel-web-policy` SHALL target the `zitadel-web` Service with probe path `/ui/v2/login`

### Requirement: Login V2 UI Calls Zitadel API via Public URL

The `zitadel-web` container SHALL set `ZITADEL_API_URL` to the public issuer URL (`https://auth.dev.liverty-music.app`), NOT the cluster-internal Service URL (`http://zitadel-api.zitadel.svc.cluster.local`).

**Rationale**: Zitadel v4 selects the virtual instance from the request's `Host` header and matches it against the configured `InstanceDomains`. The cluster-internal Service hostname is not registered as an InstanceDomain, so calls with `Host: zitadel-api.zitadel.svc.cluster.local` return HTTP 404 before reaching any handler — the Login UI's SSR sees `Failed to fetch security settings ... status:404` and returns HTTP 500. Setting `ZITADEL_API_URL` to the public URL makes the Login UI's outbound calls carry the correct `Host` header. Traffic still stays in-cluster (`zitadel-web` Pod → Gateway external IP → HTTPRoute `/` catch-all → `zitadel-api` Service); the Gateway round-trip adds ~10ms versus a direct Service hop, acceptable for dev. The naming rename (`zitadel`→`zitadel-api`, `zitadel-login`→`zitadel-web`) does not affect this behavior — it only changes the cluster-internal hostname that is, by design, NOT used here.

#### Scenario: Login UI Pod reaches Zitadel API via the public hostname

- **WHEN** the `zitadel-web` Pod issues an outbound request to fetch instance settings
- **THEN** the request URL SHALL be `https://auth.dev.liverty-music.app/...` (or the prod equivalent in prod)
- **AND** the resulting `Host` header SHALL match the configured `ExternalDomain`
- **AND** Zitadel SHALL resolve the request to the correct virtual instance

#### Scenario: Login UI does not bypass the Gateway

- **WHEN** the `zitadel-web` Pod's `ZITADEL_API_URL` is configured
- **THEN** the value SHALL be the public HTTPS URL (terminated at the Gateway)
- **AND** the value SHALL NOT be the cluster-internal Service URL — that bypass produces 404s because the Service hostname is not in `InstanceDomains`

### Requirement: Resilient Scheduling on Shared Spot Node Pool

The Zitadel API (`zitadel-api`) and Web (`zitadel-web`) Deployments SHALL each be authored against the base manifest with `replicaCount: 2`, a `PodDisruptionBudget` of `minAvailable: 1`, a required `podAntiAffinity` on `kubernetes.io/hostname`, a readiness probe pointed at the component's health endpoint (`/debug/ready` for API; `/ui/v2/login` for Web), and a rolling update strategy of `maxUnavailable: 0`. The `dev` overlay MAY relax `replicaCount` and `minAvailable` per the `optimize-dev-gke-cost` change to trade resilience for cost; the `prod` overlay SHALL inherit the base values for replica count and PDB while explicitly applying the Spot-pool `nodeSelector`.

**Rationale**: Both `dev` and `prod` overlays target the shared Spot node pool pre-launch. Base `podAntiAffinity` (hostname topology) prevents a single preemption from taking both replicas; the readiness probe holds Gateway traffic off until migrations complete. In `dev`, the `optimize-dev-gke-cost` change collapses both Deployments to `replicas: 1` and PDBs to `minAvailable: 0` — anti-affinity becomes a no-op for a single pod, and the relaxed PDB is what lets that single pod drain during node upgrades. The dev posture explicitly accepts a brief auth outage per node event for cost savings. The prod posture keeps base resilience (2 replicas, PDB ≥1) but stays on Spot until service traffic justifies non-Spot allocation.

#### Scenario: Replicas land on different nodes (base / prod)

- **WHEN** two `zitadel-api` pods are scheduled in `prod` (or in any environment whose overlay does not collapse `replicaCount` to 1)
- **THEN** they SHALL land on different Kubernetes nodes
- **AND** an unscheduled third pod (e.g., during a rollout surge) SHALL wait for a different node to become available

#### Scenario: Single-replica dev Deployment drains cleanly during node upgrade

- **WHEN** the `dev` overlay reduces `replicaCount` to 1 and PDB `minAvailable` to 0
- **AND** the cluster autoscaler or a node upgrade evicts the node hosting the Zitadel pod
- **THEN** the eviction SHALL succeed (PDB does not block)
- **AND** the Deployment SHALL re-schedule the pod onto another spot node
- **AND** the auth outage during this gap SHALL be acceptable per the dev cost posture

#### Scenario: Unready pod is excluded from Gateway backend

- **WHEN** a Zitadel pod is starting or running a migration
- **THEN** its readiness probe SHALL return non-200 until ready
- **AND** the Gateway SHALL NOT route traffic to that pod until the probe succeeds

## ADDED Requirements

### Requirement: Per-Environment Overlay Topology

The Zitadel namespace SHALL provide both `overlays/dev/` and `overlays/prod/` Kustomize overlays, each importing from `overlays/../base`, such that the renamed canonical names (`zitadel-api`, `zitadel-web`) are present in any rendered manifest tree. The `prod` overlay SHALL match the `dev` overlay's structural shape (kustomization, Deployment patches, HTTPRoute hostname patch) but SHALL NOT include resources scoped to `dev` only (notably the weekly restart CronJob marked with the `liverty-music.app/temporary` annotation).

The HTTPRoute `hostnames` field SHALL NOT appear in `base/httproute.yaml`; instead each overlay SHALL contribute a patch that supplies its environment-specific hostname (`auth.dev.liverty-music.app` for dev; `auth.liverty-music.app` for prod, treating prod as the canonical apex). Both overlays SHALL apply the Spot-pool `nodeSelector` to both Deployments.

**Rationale**: Production-readiness of the manifest topology must land in source before prod ArgoCD picks it up — otherwise prod would briefly inherit the old (pre-rename) names and immediately churn. The hostname-out-of-base discipline keeps `base/` free of environment-specific values and mirrors how `backend` and `frontend` HTTPRoutes work (no hostnames in base). The dev-only CronJob is an explicit band-aid scoped to dev's `self-hosted-zitadel` §18.6 hang; prod must not silently inherit it.

#### Scenario: Prod overlay renders the renamed resources

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered output SHALL contain a Deployment named `zitadel-api` with a container named `api`
- **AND** a Deployment named `zitadel-web` with a container named `web`
- **AND** Services named `zitadel-api` and `zitadel-web`
- **AND** PodDisruptionBudgets named `zitadel-api` and `zitadel-web`
- **AND** HealthCheckPolicies named `zitadel-api-policy` and `zitadel-web-policy`
- **AND** an HTTPRoute with `hostnames: [auth.liverty-music.app]`

#### Scenario: Dev overlay renders its hostname patch

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` is executed
- **THEN** the rendered HTTPRoute SHALL have `hostnames: [auth.dev.liverty-music.app]`
- **AND** the rendered overlay SHALL still include the dev-only `cronjob-restart-zitadel` CronJob

#### Scenario: Prod overlay omits the dev-only CronJob

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered output SHALL NOT contain any CronJob named `zitadel-restart` (or any CronJob carrying the `liverty-music.app/temporary` annotation)

#### Scenario: Prod overlay overrides env-specific values from base

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered `zitadel-web` Deployment's container env SHALL include `ZITADEL_API_URL: https://auth.liverty-music.app`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_EXTERNALDOMAIN: auth.liverty-music.app`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_DATABASE_POSTGRES_USER_USERNAME: zitadel@liverty-music-prod.iam`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_DATABASE_POSTGRES_ADMIN_USERNAME: zitadel@liverty-music-prod.iam`

#### Scenario: Base HTTPRoute has no hostnames field

- **WHEN** `base/httproute.yaml` is inspected
- **THEN** the `spec.hostnames` field SHALL be absent
- **AND** rendering the base directly (without an overlay) SHALL produce an HTTPRoute without `hostnames`

#### Scenario: Prod ArgoCD Application targets the prod overlay

- **WHEN** the ArgoCD Application source `k8s/argocd-apps/prod/zitadel.yaml` is reconciled
- **THEN** its `spec.source.path` SHALL be `k8s/namespaces/zitadel/overlays/prod`
- **AND** its `spec.syncPolicy.automated` SHALL be enabled with `prune: true` and `selfHeal: true`
