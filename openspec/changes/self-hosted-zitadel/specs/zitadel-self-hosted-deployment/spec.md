## ADDED Requirements

### Requirement: Self-Hosted Zitadel Runtime in Dev Cluster

The system SHALL run Zitadel as an in-cluster Kubernetes workload in the `dev` GKE cluster, reachable at the OIDC issuer URL `https://auth.dev.liverty-music.app`, replacing the previous dependency on a Zitadel Cloud tenant.

**Rationale**: Long-term strategy calls for self-hosted Zitadel in all environments. Running in-cluster eliminates SaaS tier constraints, gives full control over release cadence, and lets the backend reach the JWKS endpoint without leaving the cluster.

#### Scenario: Issuer reachable at the dev domain

- **WHEN** an OIDC client resolves `https://auth.dev.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.dev.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment, not Zitadel Cloud

#### Scenario: Zitadel version meets PG18 requirement

- **WHEN** the Zitadel container is started
- **THEN** the image tag SHALL be `v4.11.0` or later
- **AND** the startup SHALL succeed against the `POSTGRES_18` Cloud SQL instance

### Requirement: Two-Container Deployment with Path-Based Routing

The system SHALL deploy Zitadel as two separate Kubernetes Deployments — one for the API container (`ghcr.io/zitadel/zitadel`, port `8080`) and one for the Login V2 UI container (`ghcr.io/zitadel/login`, port `3000`) — and SHALL expose both through a single hostname via a GKE Gateway `HTTPRoute` that routes the path prefix `/ui/v2/login` to the Login Service and all other paths to the API Service.

**Rationale**: Zitadel v4 split the Login UI into a dedicated container. Keeping both on the same hostname preserves OIDC issuer identity; path-based routing avoids the extra DNS and certificate surface of a second hostname.

#### Scenario: API request reaches the API container

- **WHEN** a request arrives at `https://auth.dev.liverty-music.app/oauth/v2/keys`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel` API Service on port `8080`

#### Scenario: Login UI request reaches the Login container

- **WHEN** a browser requests `https://auth.dev.liverty-music.app/ui/v2/login/register`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-login` Service on port `3000`

### Requirement: TLS Terminated at Gateway, Cluster Traffic Unencrypted

The Zitadel API container SHALL run with `ExternalSecure: true`, `ExternalDomain: auth.dev.liverty-music.app`, `ExternalPort: 443`, and `tlsMode: external`, such that TLS is terminated by the GKE Gateway using a Google-managed certificate and cluster-internal hops use plain HTTP/h2c.

**Rationale**: This matches the existing backend ingress pattern, keeps certificate management centralized at the Gateway, and enables HTTP/2 multiplexing for in-cluster clients.

#### Scenario: Discovery document advertises HTTPS

- **WHEN** an OIDC client fetches the discovery document
- **THEN** every endpoint URL in the response SHALL use the `https://` scheme
- **AND** the port SHALL be omitted (implicit 443)

#### Scenario: In-cluster pods reach Zitadel over HTTP

- **WHEN** the backend pod fetches JWKS via the in-cluster Service DNS name
- **THEN** the connection SHALL be plain HTTP
- **AND** the connection SHALL NOT require TLS

### Requirement: Cloud SQL Connection via Auth Proxy Sidecar with IAM Authentication

Each Zitadel API pod SHALL include a Cloud SQL Auth Proxy sidecar container running with `--auto-iam-authn` and `--private-ip`, connected to the Cloud SQL instance `liverty-music-dev:asia-northeast2:postgres-osaka`, such that the Zitadel container connects to `127.0.0.1:5432` as the IAM-authenticated user `zitadel@liverty-music-dev.iam` with no password in the connection configuration.

**Rationale**: Using IAM authentication through the Auth Proxy removes the need to manage a password-bearing DSN secret, mirrors the existing backend DB-access pattern, and leverages Workload Identity for credentialless authentication.

#### Scenario: Zitadel connects to Cloud SQL without a password

- **WHEN** the Zitadel container starts
- **THEN** the configured `Database.postgres.User.Username` SHALL be `zitadel@liverty-music-dev.iam`
- **AND** `Database.postgres.User.Password` SHALL NOT be set
- **AND** `Database.postgres.Host` SHALL be `localhost`
- **AND** the connection SHALL succeed through the sidecar

#### Scenario: Zitadel skips superuser-only initialization queries

- **WHEN** the Zitadel container runs its initialization phase
- **THEN** `Database.postgres.Admin.ExistingDatabase` SHALL be `true`
- **AND** the initialization SHALL NOT attempt `CREATE ROLE` or `CREATE DATABASE`
- **AND** the initialization SHALL run schema migrations against the pre-provisioned `zitadel` database

### Requirement: Cloud SQL Database and IAM User Pre-Provisioned by Pulumi

Pulumi SHALL create the `zitadel` database and the `zitadel@liverty-music-dev.iam` Cloud SQL IAM user on the `postgres-osaka` instance, grant the IAM user ownership of the `zitadel` database, and bind Workload Identity so that the Zitadel Kubernetes Service Account can impersonate the IAM user.

#### Scenario: Database resources exist after Pulumi apply

- **WHEN** the Pulumi stack is applied
- **THEN** a database named `zitadel` SHALL exist on `postgres-osaka`
- **AND** a Cloud SQL IAM user of type `CLOUD_IAM_SERVICE_ACCOUNT` named `zitadel@liverty-music-dev.iam` SHALL exist
- **AND** the IAM user SHALL own the `zitadel` database

#### Scenario: Workload Identity binding exists

- **WHEN** the Pulumi stack is applied
- **THEN** the Kubernetes Service Account `zitadel` in namespace `zitadel` SHALL be bound to impersonate the GCP service account `zitadel@liverty-music-dev.iam.gserviceaccount.com`

### Requirement: Connection Pool Sized Within Dev Connection Budget

In the `dev` environment, the Zitadel database configuration SHALL use `MaxOpenConns: 3` and `MaxIdleConns: 1`, sized so that the total open connections per Zitadel replica fits within the dev Cloud SQL connection budget.

**Rationale**: The existing Cloud SQL `db-f1-micro` instance has a 25-connection cap; backend server (5) + backend consumer (5) + Atlas (2) already consume ~12 connections, leaving ~13 headroom. Applying the production-recommended pool of 10 per replica would exhaust the budget. The original `self-hosted-zitadel` design assumed 2 dev replicas (worst-case 6 open connections); the `optimize-dev-gke-cost` change subsequently dropped dev to 1 replica (worst-case 3 open connections) — the per-replica `MaxOpenConns: 3` value is unchanged so that re-scaling dev to 2 replicas in future remains safe without revisiting the pool.

#### Scenario: Dev Helm values carry the reduced pool

- **WHEN** the dev Kustomize overlay renders the Zitadel manifests
- **THEN** the rendered configmap or environment SHALL contain `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS=3`
- **AND** `ZITADEL_DATABASE_POSTGRES_MAXIDLECONNS=1`

### Requirement: Bootstrap Admin Machine Key Stored in Secret Manager

On first startup of an empty database, Zitadel SHALL create an initial admin machine user by consuming `ZITADEL_FIRSTINSTANCE_*` environment variables, write the resulting JWT-profile JSON key to a shared `emptyDir` pod volume, and a `bootstrap-uploader` sidecar container co-located in the same Zitadel API Pod SHALL upload that key to GCP Secret Manager as `zitadel-admin-sa-key`; subsequent Pulumi stack applies SHALL read the key from Secret Manager as the `jwtProfileJson` for the Zitadel provider.

**Rationale**: This closes the bootstrap chicken-and-egg — Pulumi needs admin credentials to configure Zitadel, but admin credentials only exist after Zitadel has bootstrapped itself. Shifting the boundary into the cluster avoids manual human steps. A separate Kubernetes `Job` cannot share an `emptyDir` volume with the Zitadel Deployment Pod (volumes are Pod-scoped), so the uploader runs as a sidecar container inside the Zitadel API Pod where the shared volume is naturally accessible. The sidecar idles after the upload (`tail -f /dev/null`) so the Pod stays ready and the upload is idempotent across Pod restarts (it skips re-uploading when the stored GSM version already matches).

#### Scenario: First boot writes the admin key

- **WHEN** the Zitadel API container starts against an empty database
- **THEN** `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH` SHALL point to a path on an `emptyDir` volume mounted into both the Zitadel container and the `bootstrap-uploader` sidecar container in the same Pod
- **AND** Zitadel SHALL write a JSON key file at that path
- **AND** the `bootstrap-uploader` sidecar container in the same Pod SHALL upload the file to GCP Secret Manager secret `zitadel-admin-sa-key`
- **AND** the `bootstrap-uploader` sidecar SHALL unlink the key file from the shared `emptyDir` after a successful GSM upload, so the org-admin private key does not persist in the volume for the Pod's lifetime where any future co-located container with the same `volumeMount` could read it

#### Scenario: Subsequent boots skip bootstrap

- **WHEN** Zitadel starts against an already-initialized database
- **THEN** the `ZITADEL_FIRSTINSTANCE_*` environment variables SHALL be ignored
- **AND** the existing admin machine user and key in Secret Manager SHALL remain unchanged

### Requirement: Masterkey Generated Once and Stored Immutably

The system SHALL generate a 32-byte Zitadel masterkey exactly once (by Pulumi's `RandomString` with `special: false`), store it in GCP Secret Manager as `zitadel-masterkey`, inject it into the Zitadel container via External Secrets Operator, and SHALL NOT rotate or regenerate it.

**Rationale**: Zitadel's event-store encryption is tied irreversibly to the masterkey; rotating or losing it renders all encrypted events unrecoverable.

#### Scenario: Masterkey exists after first Pulumi apply

- **WHEN** the Pulumi stack is applied for the first time
- **THEN** a GSM secret named `zitadel-masterkey` SHALL exist
- **AND** its value SHALL be exactly 32 bytes of alphanumeric characters

#### Scenario: Masterkey is not regenerated on subsequent applies

- **WHEN** the Pulumi stack is re-applied
- **THEN** the `zitadel-masterkey` secret value SHALL remain unchanged

### Requirement: Resilient Scheduling on Shared Spot Node Pool

The Zitadel API and Login Deployments SHALL each be authored against the base manifest with `replicaCount: 2`, a `PodDisruptionBudget` of `minAvailable: 1`, a required `podAntiAffinity` on `kubernetes.io/hostname`, a readiness probe pointed at `/debug/ready`, and a rolling update strategy of `maxUnavailable: 0`. The `dev` overlay MAY relax `replicaCount` and `minAvailable` per the `optimize-dev-gke-cost` change to trade resilience for cost; `staging` / `prod` overlays SHALL inherit the base values.

**Rationale**: The `dev` cluster uses a shared Spot node pool; on the base manifest (and in `staging` / `prod`), anti-affinity prevents a single preemption from taking both replicas, and the readiness probe holds Gateway traffic off until migrations complete. In `dev`, the `optimize-dev-gke-cost` change collapses both Deployments to `replicas: 1` and PDBs to `minAvailable: 0` — anti-affinity becomes a no-op for a single pod, and the relaxed PDB is what lets that single pod drain during node upgrades. The dev posture explicitly accepts a brief auth outage per node event for cost savings.

#### Scenario: Replicas land on different nodes (base / staging / prod)

- **WHEN** two Zitadel API pods are scheduled in `staging` or `prod` (or in any environment whose overlay does not collapse `replicaCount` to 1)
- **THEN** they SHALL land on different Kubernetes nodes
- **AND** an unscheduled third pod (e.g., during a rollout surge) SHALL wait for a different node to become available

#### Scenario: Single-replica dev Deployment drains cleanly during node upgrade

- **WHEN** the `dev` overlay reduces `replicaCount` to 1 and PDB `minAvailable` to 0
- **AND** the cluster autoscaler or a node upgrade evicts the node hosting the Zitadel pod
- **THEN** the eviction SHALL succeed (PDB does not block)
- **AND** the Deployment SHALL re-schedule the pod onto another spot node
- **AND** the auth outage during this gap SHALL be acceptable per the dev cost posture (D8)

#### Scenario: Unready pod is excluded from Gateway backend

- **WHEN** a Zitadel pod is starting or running a migration
- **THEN** its `/debug/ready` probe SHALL return non-200 until ready
- **AND** the Gateway SHALL NOT route traffic to that pod until the probe succeeds
