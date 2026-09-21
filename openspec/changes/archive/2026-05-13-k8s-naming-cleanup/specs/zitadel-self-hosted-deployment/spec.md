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

