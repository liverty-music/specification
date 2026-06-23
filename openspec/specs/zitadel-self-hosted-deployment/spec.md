# Zitadel Self-Hosted Deployment

## Purpose

Run Zitadel as an in-cluster Kubernetes workload in the GKE cluster
(replacing the prior Zitadel Cloud SaaS dependency), reachable at the
environment's OIDC issuer URL. Captures the runtime, networking,
database, secrets, and resilience invariants for the self-hosted
Zitadel instance — including the bootstrap chicken-and-egg resolution,
the masterkey immutability constraint, and the post-cutover incident
findings on backend MachineKey lifecycle.
## Requirements
### Requirement: Self-Hosted Zitadel Runtime in Each Environment Cluster

The system SHALL run Zitadel as an in-cluster Kubernetes workload in each environment's GKE cluster (`dev` and `prod`), reachable at the environment-specific OIDC issuer URL, replacing the previous dependency on a Zitadel Cloud tenant.

| Environment | Cluster | OIDC issuer |
|---|---|---|
| `dev` | `standard-cluster-osaka` (`liverty-music-dev`) | `https://auth.dev.liverty-music.app` |
| `prod` | `autopilot-cluster-osaka` (`liverty-music-prod`) | `https://auth.liverty-music.app` |

**Rationale**: Long-term strategy calls for self-hosted Zitadel in all environments. Running in-cluster eliminates SaaS tier constraints, gives full control over release cadence, and lets the backend reach the JWKS endpoint without leaving the cluster. The `prod-k8s-manifests` change extends this requirement (originally dev-scoped under the `self-hosted-zitadel` change) to also cover the prod cluster after `migrate-prod-to-autopilot` brought the prod Autopilot cluster online.

#### Scenario: Issuer reachable at the dev domain

- **WHEN** an OIDC client resolves `https://auth.dev.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.dev.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment in the dev cluster, not Zitadel Cloud

#### Scenario: Issuer reachable at the prod domain

- **WHEN** an OIDC client resolves `https://auth.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment in the prod cluster, not Zitadel Cloud

#### Scenario: Zitadel version meets PG18 requirement

- **WHEN** the Zitadel container is started in either env
- **THEN** the image tag SHALL be `v4.11.0` or later
- **AND** the startup SHALL succeed against the `POSTGRES_18` Cloud SQL instance

#### Scenario: Prod Zitadel uses prod Cloud SQL + prod GSM secrets

- **WHEN** inspecting the rendered `k8s/namespaces/zitadel/overlays/prod/` manifests
- **THEN** the `cloud-sql-proxy` sidecar SHALL connect to the prod Cloud SQL instance `liverty-music-prod:asia-northeast2:postgres-osaka`
- **AND** the `ExternalSecret` resources SHALL reference the `liverty-music-prod` GSM secrets `zitadel-masterkey` and `zitadel-machine-key-for-pulumi-admin` (the canonical names provisioned by `SecretsComponent` per the existing `Bootstrap Admin Machine Key Stored in Secret Manager` requirement) via the prod-scoped `ClusterSecretStore`
- **AND** the `zitadel-masterkey` GSM Secret SHALL have a Pulumi-managed first version (random 32-char string) by the time the first Zitadel API Pod boots
- **AND** the `zitadel-machine-key-for-pulumi-admin` GSM Secret SHALL exist as an empty shell at first boot — the in-cluster `bootstrap-uploader` sidecar populates it automatically on first-instance Zitadel bootstrap; no human pre-seed is required

### Requirement: Two-Container Deployment with Path-Based Routing

The system SHALL deploy Zitadel as two separate Kubernetes Deployments — one for the API container (`ghcr.io/zitadel/zitadel`, port `8080`, Deployment name `zitadel-api`) and one for the Login V2 UI container (`ghcr.io/zitadel/zitadel-login`, port `3000`, Deployment name `zitadel-api-login`) — and SHALL expose both through a single hostname via a GKE Gateway `HTTPRoute` that routes the path prefix `/ui/v2/login` to the Login UI Service (`zitadel-api-login`) and all other paths to the API Service (`zitadel-api`). Both Deployments SHALL be rendered by the official `zitadel/zitadel-charts` Helm chart with `fullnameOverride: zitadel-api` (NOT hand-written manifests under `k8s/namespaces/zitadel/base/`).

**Rationale**: Zitadel v4 split the Login UI into a dedicated container. Keeping both on the same hostname preserves OIDC issuer identity; path-based routing avoids the extra DNS and certificate surface of a second hostname. The API Deployment / Service is named `zitadel-api` to avoid the legacy `ZITADEL_PORT` env-var Viper collision that would occur with the chart-default `zitadel` name (Kubernetes' service-discovery env-var injection would inject `ZITADEL_PORT=tcp://<ip>:80` which Viper parses as the binary's `Port` config field — startup fails). The Login UI Deployment / Service is named `zitadel-api-login` because the chart hard-codes the Login UI's resource name to `<zitadel.fullname>-login` regardless of `login.fullnameOverride`. The image path is `ghcr.io/zitadel/zitadel-login`, NOT `ghcr.io/zitadel/login` (the latter 404s); the upstream Helm chart default uses the same path. Rendering via the official chart eliminates the divergence from upstream defaults that hand-tuned manifests accumulated.

#### Scenario: API request reaches the API container

- **WHEN** a request arrives at `https://auth.dev.liverty-music.app/oauth/v2/keys`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-api` Service on port `80` (Service targetPort 8080)

#### Scenario: Login UI request reaches the Login UI container

- **WHEN** a browser requests `https://auth.dev.liverty-music.app/ui/v2/login/register`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-api-login` Service on port `80` (Service targetPort 3000)

#### Scenario: HealthCheckPolicy targets chart-natural Service names

- **WHEN** the GKE Gateway evaluates backend health
- **THEN** a `HealthCheckPolicy` named `zitadel-api-policy` SHALL target the `zitadel-api` Service with probe path `/debug/healthz`
- **AND** a `HealthCheckPolicy` named `zitadel-web-policy` SHALL target the `zitadel-api-login` Service with probe path `/ui/v2/login/healthy` (the resource name `zitadel-web-policy` is retained for ops continuity; the targetRef is updated but the probe path keeps the chart-default base — see the "Login V2 UI URL is `/ui/v2/login/login`" accepted-state note below)

#### Scenario: Both Deployments are chart-rendered with the expected names

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** both Deployments SHALL carry the `app.kubernetes.io/managed-by: Helm` label
- **AND** their `metadata.name` SHALL be `zitadel-api` (top-level `fullnameOverride`) and `zitadel-api-login` (chart-hard-coded `<fullname>-login`)

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

Pulumi SHALL create the `zitadel` database and the `zitadel@liverty-music-${env}.iam` Cloud SQL IAM user on the `postgres-osaka` instance (where `${env}` is `dev` or `prod`), grant the IAM user ownership of the `zitadel` database, and bind Workload Identity so that the Zitadel Kubernetes Service Account can impersonate the IAM user.

#### Scenario: Database resources exist after Pulumi apply

- **WHEN** the Pulumi stack is applied
- **THEN** a database named `zitadel` SHALL exist on `postgres-osaka`
- **AND** a Cloud SQL IAM user of type `CLOUD_IAM_SERVICE_ACCOUNT` named `zitadel@liverty-music-${env}.iam` SHALL exist (matching the stack's environment)
- **AND** the IAM user SHALL own the `zitadel` database

#### Scenario: Workload Identity binding exists

- **WHEN** the Pulumi stack is applied
- **THEN** the Kubernetes Service Account `zitadel` in namespace `zitadel` SHALL be bound to impersonate the GCP service account `zitadel@liverty-music-${env}.iam.gserviceaccount.com` (matching the stack's environment)

### Requirement: Connection Pool Sized Within Dev Connection Budget

In the `dev` environment, the Zitadel database configuration SHALL use `MaxOpenConns: 3` and `MaxIdleConns: 1`, sized so that the total open connections per Zitadel replica fits within the dev Cloud SQL connection budget.

**Rationale**: The existing Cloud SQL `db-f1-micro` instance has a 25-connection cap; backend server (5) + backend consumer (5) + Atlas (2) already consume ~12 connections, leaving ~13 headroom. Applying the production-recommended pool of 10 per replica would exhaust the budget. The original `self-hosted-zitadel` design assumed 2 dev replicas (worst-case 6 open connections); the `optimize-dev-gke-cost` change subsequently dropped dev to 1 replica (worst-case 3 open connections) — the per-replica `MaxOpenConns: 3` value is unchanged so that re-scaling dev to 2 replicas in future remains safe without revisiting the pool.

#### Scenario: Dev Helm values carry the reduced pool

- **WHEN** the dev Kustomize overlay renders the Zitadel manifests
- **THEN** the rendered configmap or environment SHALL contain `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS=3`
- **AND** `ZITADEL_DATABASE_POSTGRES_MAXIDLECONNS=1`

### Requirement: Bootstrap Admin Machine Key Stored in Secret Manager

On first startup of an empty database, Zitadel SHALL create an initial admin machine user by consuming `ZITADEL_FIRSTINSTANCE_*` environment variables, write the resulting JWT-profile JSON key to a shared `emptyDir` pod volume, and a `bootstrap-uploader` sidecar container co-located in the same Zitadel API Pod SHALL upload that key to GCP Secret Manager as `zitadel-machine-key-for-pulumi-admin`; subsequent Pulumi stack applies SHALL read the key from Secret Manager as the `jwtProfileJson` for the Zitadel provider. This lifecycle SHALL apply identically across all environments (`dev` and `prod`).

Per the `Single Unified Zitadel Class Across All Environments` requirement, the JWT read + Provider construction live inside one shared `Zitadel` class consumed by all Pulumi stacks. No per-env wrapper class (`BackendMachineKeyComponent`, `ZitadelProdStackComponent`) shall mediate this lifecycle.

**Rationale**: This closes the bootstrap chicken-and-egg — Pulumi needs admin credentials to configure Zitadel, but admin credentials only exist after Zitadel has bootstrapped itself. Shifting the boundary into the cluster avoids manual human steps. A separate Kubernetes `Job` cannot share an `emptyDir` volume with the Zitadel Deployment Pod (volumes are Pod-scoped), so the uploader runs as a sidecar container inside the Zitadel API Pod where the shared volume is naturally accessible. The sidecar idles after the upload (`tail -f /dev/null`) so the Pod stays ready and the upload is idempotent across Pod restarts (it skips re-uploading when the stored GSM version already matches).

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`, where `<principal>` is the Pulumi `MachineUser` resource id. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

The unified `Zitadel` class refactor (`refactor-unify-env-dispatch`) deletes the prod-specific `BackendMachineKeyComponent` that previously mediated this for prod. The unified class re-runs the same GSM read + Provider construction in both envs from a single code path; the `pulumi.secret()` wrap that protects the embedded RSA private key from leaking into preview/state/log output is enforced once in the unified class and inherited by all envs.

#### Scenario: First boot writes the admin key

- **WHEN** the Zitadel API container starts against an empty database
- **THEN** `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH` SHALL point to a path on an `emptyDir` volume mounted into both the Zitadel container and the `bootstrap-uploader` sidecar container in the same Pod
- **AND** Zitadel SHALL write a JSON key file at that path
- **AND** the `bootstrap-uploader` sidecar container in the same Pod SHALL upload the file to GCP Secret Manager secret `zitadel-machine-key-for-pulumi-admin`
- **AND** the `bootstrap-uploader` sidecar SHALL unlink the key file from the shared `emptyDir` after a successful GSM upload, so the org-admin private key does not persist in the volume for the Pod's lifetime where any future co-located container with the same `volumeMount` could read it

#### Scenario: Subsequent boots skip bootstrap

- **WHEN** Zitadel starts against an already-initialized database
- **THEN** the `ZITADEL_FIRSTINSTANCE_*` environment variables SHALL be ignored
- **AND** the existing admin machine user and key in Secret Manager SHALL remain unchanged

#### Scenario: Unified Zitadel class reads admin JWT in all envs

- **WHEN** `pulumi up` runs for any env after the `refactor-unify-env-dispatch` change is applied
- **THEN** the JWT is read via `gcp.secretmanager.getSecretVersionAccessOutput` against the env-scoped `zitadel-machine-key-for-pulumi-admin` GSM Secret
- **AND** the read result is wrapped in `pulumi.secret()` inside the unified `Zitadel` class
- **AND** the wrapped value is passed to `new zitadel.Provider(...).jwtProfileJson`
- **AND** no env-specific wrapper class mediates this construction

### Requirement: Backend MachineKey Lifecycle Tied to Zitadel-Side Identity

The backend's machine-user JWT private key (`zitadel-machine-key-for-backend-app` in GSM) SHALL track the `MachineKey` Pulumi resource's `keyDetails` output one-to-one. State drift between the Zitadel DB, the GSM SecretVersion, and the Pulumi state SHALL be treated as a critical incident — backend → Zitadel API auth fails with `Errors.AuthNKey.NotFound` whenever the kid in the GSM-mounted JSON key does not have a matching row in Zitadel's AuthNKey table. This lifecycle SHALL apply identically in dev and prod; both stacks SHALL produce a `MachineKey` resource and a corresponding GSM SecretVersion (`zitadel-machine-key-for-backend-app` in their respective GCP projects).

**Rationale**: Discovered post-cutover when `ResendEmailVerification` returned `Errors.Internal (OIDC-AhX2u) parent: invalid signature (error fetching keys: Errors.AuthNKey.NotFound)`. The cause was a three-way drift after the cutover incident chain:

1. Pulumi created a fresh self-hosted MachineKey at v252; GSM was updated with the new keyDetails.
2. `pulumi state delete --target-dependents` cascade-removed the MachineKey state at v250.
3. The merged-state import at v254 re-injected the v246 (Cloud-era) MachineKey output into Pulumi state.
4. v258's SecretVersion replace pulled `secretData` from the (now stale) `MachineKey.keyDetails`, writing the Cloud-era key back into GSM. Zitadel DB still held the self-hosted key.

The fix (cloud-provisioning#216) was to force-replace the `MachineKey` resource by changing `expirationDate` from the magic upstream-example value `2519-04-01T08:45:00Z` to a clean `2099-01-01T00:00:00Z`. Replacement re-runs the create flow, which produces a fresh `keyDetails` value that propagates through the dependency graph.

The GSM name `zitadel-machine-key-for-backend-app` follows the platform-wide convention `zitadel-machine-key-for-<principal>`. The legacy name `zitadel-machine-key` was renamed because (1) it did not encode which Zitadel principal owned the key, ambiguity that directly cost triage time in the §13.15 incident chain, and (2) the platform now manages two Zitadel `MachineKey`s (`pulumi-admin` and `backend-app`) that need to be distinguishable at a glance.

#### Scenario: keyId in GSM matches Zitadel DB

- **WHEN** Pulumi state contains a `MachineKey` for a given user
- **THEN** the `keyId` in the GSM SecretVersion's JSON SHALL match a row in Zitadel's AuthNKey table for that user
- **AND** backend → Zitadel API JWT bearer auth SHALL succeed

#### Scenario: Force-replace on detected drift

- **WHEN** the operator detects keyId drift (e.g., via `Errors.AuthNKey.NotFound` in backend logs)
- **THEN** the operator SHALL force-replace the Pulumi `MachineKey` resource by changing a non-cosmetic property (e.g., bumping `expirationDate` to a different valid value)
- **AND** the resulting Pulumi apply SHALL produce a new `keyDetails` value, propagate it through the dependency graph, replace the GSM SecretVersion, sync ESO, and trigger Reloader-driven backend Pod restart

#### Scenario: Both dev and prod produce a Backend MachineKey

- **WHEN** `pulumi up` runs for the `dev` stack and again for the `prod` stack
- **THEN** each stack's resulting Pulumi state SHALL contain exactly one `MachineKey` resource for the `backend-app` machine user
- **AND** each stack's GSM project (`liverty-music-dev` and `liverty-music-prod` respectively) SHALL contain a Secret named `zitadel-machine-key-for-backend-app` with at least one enabled SecretVersion

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

The Zitadel API (`zitadel-api`) and Web (`zitadel-web`) Deployments SHALL each be authored against the base manifest with a `PodDisruptionBudget`, a readiness probe pointed at the component's health endpoint (`/debug/ready` for API; `/ui/v2/login` for Web), and a rolling update strategy of `maxUnavailable: 0`. The base manifest MAY be single-replica for cost-simplicity; the `dev` overlay MAY run `replicaCount: 1` with PDB `minAvailable: 0` per the `optimize-dev-gke-cost` change. The **`prod` overlay SHALL explicitly set `replicaCount: 2` and PDB `minAvailable: 1`** for `zitadel-api`, and the running prod state SHALL match it — a prod `zitadel-api` observed at `replicas: 1` is a drift to be corrected, not an accepted posture. `podAntiAffinity` is OPTIONAL at the current resource size (GKE Autopilot rejects it below the CPU floor); it is a node-failure concern separate from the per-process wedge that ≥2 replicas address.

The readiness probe (`/debug/ready`) protects traffic against **startup and migration** unreadiness only. It SHALL NOT be relied upon to remove a pod suffering the in-process projection-trigger wedge (zitadel/zitadel#10103): a wedged pod keeps `/debug/ready` and `/debug/healthz` at 200 while auth-flow requests hang. Recovery from that wedge is delegated to the self-healing watchdog (see "Self-healing watchdog auto-restarts a wedged Zitadel API"); the prod ≥2-replica posture exists to bound the wedge blast radius to a single pod and to make the watchdog's rolling restart non-disruptive.

**Rationale**: Both overlays target the shared Spot node pool pre-launch. In `dev`, the `optimize-dev-gke-cost` change runs a single replica with a relaxed PDB and accepts a brief auth outage per node event for cost savings. The 2026-06-23 prod outage showed that a single wedged replica (prod was running 1) takes down all login because readiness cannot detect the wedge — hence the explicit prod `replicaCount: 2` clause and the delegation of wedge-recovery to the watchdog. Two replicas alone do not auto-heal (a wedged-but-ready pod still serves and hangs ~half of logins), but they keep one replica serving while the watchdog restarts the other.

#### Scenario: Prod runs two replicas

- **WHEN** an operator inspects the running `zitadel-api` Deployment in `prod`
- **THEN** its `spec.replicas` SHALL be 2 and its PDB `minAvailable` SHALL be 1
- **AND** a value of 1 SHALL be treated as drift and reconciled

#### Scenario: Single-replica dev Deployment drains cleanly during node upgrade

- **WHEN** the `dev` overlay runs `replicaCount: 1` with PDB `minAvailable: 0`
- **AND** a node upgrade evicts the node hosting the Zitadel pod
- **THEN** the eviction SHALL succeed (PDB does not block)
- **AND** the Deployment SHALL re-schedule the pod onto another spot node
- **AND** the auth outage during this gap SHALL be acceptable per the dev cost posture

#### Scenario: Unready pod is excluded from Gateway backend

- **WHEN** a Zitadel pod is starting or running a migration
- **THEN** its readiness probe SHALL return non-200 until ready
- **AND** the Gateway SHALL NOT route traffic to that pod until the probe succeeds

#### Scenario: Wedged-but-ready pod is recovered by the watchdog, not readiness

- **WHEN** a `zitadel-api` pod is suffering the projection-trigger wedge (auth-flow requests hang) but `/debug/ready` still returns 200
- **THEN** the Gateway SHALL continue routing to that pod (readiness does not detect the wedge)
- **AND** recovery SHALL come from the self-healing watchdog restarting the pod, with the second replica absorbing traffic during the rolling restart

### Requirement: GSM Naming Convention for Zitadel MachineKey Credentials

GSM secrets that store a Zitadel `MachineKey` JWT private key SHALL follow the naming convention `zitadel-machine-key-for-<principal>`, where `<principal>` is the Pulumi `MachineUser` resource id (matching the Zitadel `userName`).

**Rationale**: A uniform convention encodes the resource type (Zitadel `MachineKey`) and the owning principal in the GSM secret name itself. The `for-` preposition signals that the suffix is the *owning principal*, not the *consuming system* — important because the principal name (e.g., `backend-app`) is intentionally shared across multiple identity systems (K8s ServiceAccount, GCP IAM ServiceAccount, Zitadel MachineUser). Operators inspecting GSM and developers reading code can identify the principal binding at a glance, without grepping call sites.

#### Scenario: Existing MachineKey credentials follow the convention

- **WHEN** an operator lists Zitadel-related GSM secrets in the dev project
- **THEN** every secret containing a Zitadel `MachineKey` JWT private key SHALL have a name matching `zitadel-machine-key-for-<principal>`
- **AND** `<principal>` SHALL match a `zitadel.MachineUser` resource id present in Pulumi state

#### Scenario: New MachineUser provisioning adopts the convention

- **WHEN** Pulumi adds a new `zitadel.MachineUser` + `zitadel.MachineKey` pair for a new service identity
- **THEN** the associated GSM secret SHALL be named `zitadel-machine-key-for-<new-principal>`
- **AND** no alternative naming SHALL be used for new credentials

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
- **AND** the rendered overlay SHALL still include the dev-only `zitadel-restart` CronJob (carrying the `liverty-music.app/temporary` annotation)

#### Scenario: Prod overlay omits the dev-only CronJob

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered output SHALL NOT contain any CronJob named `zitadel-restart` (or any CronJob carrying the `liverty-music.app/temporary` annotation)

#### Scenario: Prod overlay overrides env-specific values from base

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered `zitadel-web` Deployment's container env SHALL include `ZITADEL_API_URL: https://auth.liverty-music.app`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_EXTERNALDOMAIN: auth.liverty-music.app`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_DATABASE_POSTGRES_USER_USERNAME: zitadel@liverty-music-prod.iam`
- **AND** the rendered `zitadel-config` ConfigMap SHALL have `ZITADEL_DATABASE_POSTGRES_ADMIN_USERNAME: zitadel@liverty-music-prod.iam`
- **AND** the rendered `zitadel` ServiceAccount SHALL have `annotations."iam.gke.io/gcp-service-account": zitadel@liverty-music-prod.iam.gserviceaccount.com`
- **AND** the rendered `zitadel-api` Deployment's `cloud-sql-proxy` container SHALL have its positional instance-connection-name arg set to `liverty-music-prod:asia-northeast2:postgres-osaka` (not the dev value)

#### Scenario: Dev-only DB grant Job stays out of prod

- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` is executed
- **THEN** the rendered output SHALL NOT contain a Job named `zitadel-db-grant` (that Job lives in `overlays/dev/` because it hardcodes the dev Cloud SQL instance and dev IAM SA username)
- **WHEN** `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` is executed
- **THEN** the rendered output SHALL contain the `zitadel-db-grant` Job

#### Scenario: Base HTTPRoute has no hostnames field

- **WHEN** `base/httproute.yaml` is inspected
- **THEN** the `spec.hostnames` field SHALL be absent
- **AND** rendering the base directly (without an overlay) SHALL produce an HTTPRoute without `hostnames`

#### Scenario: Prod ArgoCD Application targets the prod overlay

- **WHEN** the ArgoCD Application source `k8s/argocd-apps/prod/zitadel.yaml` is reconciled
- **THEN** its `spec.source.path` SHALL be `k8s/namespaces/zitadel/overlays/prod`
- **AND** its `spec.syncPolicy.automated` SHALL be enabled with `prune: true` and `selfHeal: true`

### Requirement: Single Unified Zitadel Class Across All Environments

The Pulumi `cloud-provisioning` codebase SHALL provision the Zitadel application stack via a **single** `Zitadel` class (`src/zitadel/index.ts`) used by every Pulumi stack. The class SHALL accept an `env: Environment` argument and SHALL handle all environment-specific behavior internally via ternary expressions and `Record<Environment, T>` constant maps. Parallel "prod-only" or "env-specific" wrapper classes (e.g., `BackendMachineKeyComponent`, `ZitadelProdStackComponent`) SHALL NOT exist; the call-site in `src/index.ts` SHALL invoke `new Zitadel(name, { env, ... })` once, without env-branching.

**Rationale**: The previous parallel-class pattern (`BackendMachineKeyComponent` from `enable-zitadel-prod-pulumi-provider`, `ZitadelProdStackComponent` from `complete-zitadel-prod-pulumi-stack`) duplicated the 9-component Zitadel topology across two near-identical class definitions. Every future Zitadel-side change had to be applied in both places with no compiler-level synchronization guarantee. The leaf components already accept `env` and switch behavior internally via env-keyed maps (`baseDomainMap`, `zitadelDomainMap`, `senderAddressMap`); the wrappers fought that grain. A single class with env-aware internals fits the established leaf-component pattern and eliminates the drift hazard.

#### Scenario: Single Zitadel class instantiation in src/index.ts

- **WHEN** `cloud-provisioning/src/index.ts` is inspected
- **THEN** it SHALL contain exactly one `new Zitadel(...)` instantiation
- **AND** the instantiation SHALL NOT be wrapped in an `if (env === ...)` branch
- **AND** no other `zitadel:liverty-music:*` ComponentResource wrapping the 9 Zitadel leaf components SHALL exist

#### Scenario: Env-driven differences via map / ternary, not branching wrapper

- **WHEN** the `Zitadel` class constructor handles an environment-specific value (admin org id, redirect URI, sender address, etc.)
- **THEN** the value SHALL be sourced from a `Record<Environment, T>` map (e.g., `adminOrgIdMap`, `baseDomainMap`) consulted via `[env]` indexing
- **AND/OR** the value SHALL be a ternary expression (`env === 'dev' ? X : Y`)
- **AND** the class SHALL NOT have its own `if (env === 'dev')` / `if (env === 'prod')` top-level dispatch (env-conditional leaf-component instantiation such as `if (env === 'dev') this.e2eTestUser = ...` is acceptable when the leaf component is truly env-scoped, but the wrapper structure itself is uniform)

#### Scenario: Zero dev URN churn after unification

- **WHEN** `pulumi preview --stack dev` runs after this requirement is implemented
- **THEN** the preview SHALL show zero changes to existing Zitadel-side resource URNs in dev state
- **AND** the `Zitadel` class internal structure SHALL be byte-equivalent to its pre-refactor form modulo the removal of the `env !== 'dev'` throw guard and the addition of env-conditional `E2eTestUserComponent` creation

### Requirement: Per-Environment Configuration Values Sourced From Env-Keyed Map

Environment-keyed configuration values that vary across stacks (admin org ids, redirect URI lists, sender addresses, cluster names for monitoring filters, etc.) SHALL be expressed as `Record<Environment, T>` constant maps and looked up via `[env]` indexing, OR as inline ternary expressions on `env`. Per-env scalar constants (such as a legacy `ZITADEL_DEV_ADMIN_ORG_ID` covering only one env) SHALL NOT be used when a corresponding value is needed for additional envs.

**Rationale**: Localizing env-keyed differences in a single map forces the env-specific value to be the only thing that varies. Future env additions update the map; future env removals delete an entry. The alternative — duplicating surrounding code per-env branch — has historically led to drift (e.g., the `MonitoringComponent` clusterName hardcoded to a dev-only value, which silently routed prod alerts to the wrong cluster).

**Out-of-scope for this requirement** (not a SHALL): general code-style preferences such as "use ternary spread over `if-push`" for array construction. Those are coding conventions tracked outside the capability spec, because their verifiability depends on judgment calls that no spec scenario can pin down.

#### Scenario: Admin org id sourced from env-keyed map

- **WHEN** the `Zitadel` class imports the admin org via `zitadel.Org('admin', ...)` resource option `import:`
- **THEN** the import id SHALL be `adminOrgIdMap[env]` where `adminOrgIdMap: Record<Environment, string>` lives in `src/zitadel/constants.ts`
- **AND** the map SHALL contain entries for every env in `Environment` type union (at minimum `dev` + `prod`)
- **AND** no per-env scalar constant (such as a legacy `ZITADEL_DEV_ADMIN_ORG_ID`) SHALL be referenced

#### Scenario: MonitoringComponent cluster targeting via env-keyed map

- **WHEN** `MonitoringComponent` is instantiated for any env
- **THEN** its `clusterName` and `clusterLocation` arguments SHALL be sourced from env-keyed maps (e.g., `clusterNameByEnv`, `clusterLocationByEnv`) or inline ternaries
- **AND** the resolved values SHALL match the cluster actually deployed in that env (dev: `standard-cluster-osaka` / `asia-northeast2-a`; prod: `autopilot-cluster-osaka` / `asia-northeast2`)
- **AND** no per-cluster name SHALL be hardcoded to a single env's value

#### Scenario: places.googleapis.com enabled in all environments

- **WHEN** `src/gcp/components/kubernetes.ts` builds the `apisToEnable` list
- **THEN** `places.googleapis.com` SHALL be included unconditionally (no env-gated `apisToEnable.push`)

### Requirement: Backend MachineUser Lives in Product Org Across All Environments

The Pulumi `Zitadel` class SHALL create the backend `MachineUser` (with `ORG_USER_MANAGER` role grant via `OrgMember`) inside a **Pulumi-managed product org** named `liverty-music`, in every environment. Pulumi SHALL NOT create or manage the first-boot admin org (auto-created by Zitadel via `ZITADEL_FIRSTINSTANCE_ORG_NAME`) as a creation; the admin org SHALL be brought into Pulumi state via the `import:` resource option using an environment-keyed admin-org-id map (`adminOrgIdMap`), without per-env wrapper classes or per-env scalar constants.

**Rationale**: The first-boot admin org holds operator identities — `pulumi-admin` (IaC break-glass), `login-client` (Login V2 PAT host), and any human IAM_OWNER admins. Granting the backend `MachineUser` `ORG_USER_MANAGER` in that org would let the runtime backend Pod create, suspend, or modify those operator identities — a privilege-escalation foothold from a compromised backend Pod to the IaC/admin tier. Placing `backend-app` in a separate Pulumi-managed product org confines `ORG_USER_MANAGER` to end-user principals. This rule applied to dev from the original cutover (`add-zitadel-console-admin-via-google-idp`) and was extended to prod in `enable-zitadel-prod-pulumi-provider` with the prod-specific `BackendMachineKeyComponent`. The unified `Zitadel` class makes the rule env-agnostic: same code path, same Pulumi resource shapes, env-specific values only via maps.

#### Scenario: backend-app MachineUser lives in product org (any env)

- **WHEN** `pulumi up` is applied to any env (`dev` or `prod`)
- **THEN** the resulting Pulumi state SHALL contain exactly one `zitadel.Org` resource named `liverty-music` (the product org)
- **AND** the backend `zitadel.MachineUser` resource SHALL reference `productOrg.id`, NOT the admin org's id
- **AND** the `zitadel.OrgMember` granting `ORG_USER_MANAGER` SHALL also scope to `productOrg.id`

#### Scenario: Admin org imported via inline import: resource option, env-keyed id

- **WHEN** the `Zitadel` class instantiates `new zitadel.Org('admin', ...)` for any env
- **THEN** the resource SHALL declare `protect: true`
- **AND** SHALL declare `isDefault: true` (matching the bootstrap-set flag)
- **AND** SHALL declare `import: adminOrgIdMap[env]` to bind to the pre-existing bootstrap-created admin org
- **AND** the `adminOrgIdMap` SHALL contain at minimum a `dev` entry and a `prod` entry, each set to the respective env's admin-org-id as discovered post-bootstrap via `POST /admin/v1/orgs/_search`

#### Scenario: Provider sourced from GSM admin JWT in all envs

- **WHEN** the `Zitadel` class instantiates `new zitadel.Provider(...)` for any env
- **THEN** `jwtProfileJson` SHALL be a `pulumi.secret()`-wrapped `Output<string>` produced by `gcp.secretmanager.getSecretVersionAccessOutput` against the GSM Secret `zitadel-machine-key-for-pulumi-admin` in the env's GCP project
- **AND** the env's `domain` SHALL be `zitadelDomainMap[env]`
- **AND** no per-env wrapper class SHALL pre-process or shadow this Provider construction

### Requirement: Cost Guardrails and Observability Applied to All Environments

The Pulumi `cloud-provisioning` codebase SHALL instantiate `ZitadelMonitoringComponent` and `gcp.billing.Budget` in every environment (`dev` and `prod`). Materialization of these resources at apply time SHALL be gated by the presence of their required ESC configuration (`gcpConfig.monitoring?.slackNotificationChannels` for the monitoring chain; `gcpConfig.billingAlertEmail` for the budget), not by env-hardcoded branches.

**Rationale**: The previous `if (environment === 'dev')` guard around `ZitadelMonitoringComponent` and the billing budget was a pre-prod decision rationalized as "thresholds tuned for dev, would page on prod". Empirically the thresholds (50× headroom on latency p99, 10 errors / 60s on JWT validation) are generous enough for pre-launch prod traffic. Re-tuning is a future operational concern; gating on env at code level prevents the operator from enabling prod alerts via ESC seeding without a code change. The new pattern: code is env-uniform, materialization is ESC-driven.

#### Scenario: ZitadelMonitoringComponent runs in all envs when Slack channel ESC seeded

- **WHEN** `pulumiConfig.gcp.monitoring.slackNotificationChannels.alertBackend` is seeded in an env's ESC
- **THEN** `pulumi up` for that env SHALL create the `ZitadelMonitoringComponent` resources (latency p99 alert, JWT error rate alert, connection-pool dashboard)
- **AND** no `if (environment === 'dev')` code branch SHALL gate the instantiation

#### Scenario: Billing budget materializes when ESC seeded, any env

- **WHEN** `gcpConfig.billingAlertEmail` is set in an env's ESC
- **THEN** `pulumi up` for that env SHALL create a `gcp.billing.Budget` resource named `cost-budget` (env scoping is via Pulumi stack URN, not the resource name)
- **AND** the budget amount SHALL be sourced from `gcpConfig.budgetAmountJpy` (new field, env-specific value)

#### Scenario: MonitoringComponent targets the env's actual cluster

- **WHEN** `MonitoringComponent` instantiates log-based alert policies
- **THEN** the `clusterName` and `clusterLocation` arguments SHALL be sourced from env-keyed maps (e.g., `clusterNameByEnv`, `clusterLocationByEnv`)
- **AND** the resolved values SHALL match the cluster actually deployed in that env (dev: `standard-cluster-osaka` / `asia-northeast2-a`; prod: `autopilot-cluster-osaka` / `asia-northeast2`)
- **AND** no per-cluster name SHALL be hardcoded to a single env's value

> **Accepted as the operational state: Login V2 UI URL is
> `/ui/v2/login/login`.** The `migrate-zitadel-to-helm-chart` change
> attempted to collapse the redundant `/ui/v2/login/login` URL down
> to `/ui/v2/login` by setting `NEXT_PUBLIC_BASE_PATH=/ui/v2` at
> runtime on the Login UI Pod + matching probe paths + HTTPRoute
> prefix + `DefaultInstance.Features.LoginV2.BaseURI: /ui/v2`. The
> collapse CrashLooped the Login UI on the prod cutover:
> `NEXT_PUBLIC_*` env vars in Next.js are inlined at IMAGE BUILD
> time, so the v4.14.0 `zitadel-login` image kept serving at its
> baked-in `/ui/v2/login/*` regardless of our runtime override — our
> probes at `/ui/v2/{healthy,ready}` got 404 and the Pod was killed.
> Reverted via cloud-provisioning #299.
>
> The redundant `/ui/v2/login/login` URL is **accepted as the
> permanent operational state**, NOT tracked as a future change. A
> proper collapse would require either rebuilding the upstream image
> with a different `NEXT_PUBLIC_BASE_PATH` set at build time
> (ongoing fork-maintenance cost), OR adding a Gateway URLRewrite
> mapping `/ui/v2/login` → `/ui/v2/login/login` server-side (added
> routing complexity for purely cosmetic gain). Neither risk/cost is
> justified against a URL the end-user only sees during sign-in
> flow. If a future Zitadel upstream release changes the
> Login UI's base path, this note may become re-relevant.
>
> See archive `openspec/changes/archive/2026-05-20-migrate-zitadel-to-helm-chart/tasks.md`
> "Deployment-incident postscript" §D for the full incident timeline.

### Requirement: Zitadel Deployment Rendered by Official Helm Chart

The Zitadel API and Login V2 UI Deployments, Services, ServiceAccounts, PodDisruptionBudgets, and ConfigMap SHALL be rendered from the official `zitadel/zitadel-charts` Helm chart via Kustomize's `helmCharts:` integration (pinned to a specific chart version in each overlay's `kustomization.yaml`), NOT hand-written. The chart's top-level `fullnameOverride: zitadel-api` SHALL preserve the API Deployment / Service / ConfigMap names; the Login V2 UI subchart hard-codes its resource name to `<zitadel.fullname>-login` (i.e., `zitadel-api-login`) — `login.fullnameOverride` exists as a values key but is NOT honored by the chart templates. HTTPRoute backendRefs and HealthCheckPolicy targets SHALL be updated to reference `zitadel-api-login` for the Login UI side; the API side remains `zitadel-api`.

**Rationale**: The Helm chart is the upstream-supported deployment artifact for Zitadel self-hosting. Hand-rolled Kustomize Deployments diverge from upstream defaults at every release. The `helmCharts:` integration pattern is already in use for `external-secrets`, `reloader`, `nats`, `keda`, and `atlas-operator`, so adopting it for Zitadel keeps the manifest tree internally consistent. The `fullnameOverride: zitadel-api` (not the chart-default `zitadel`) avoids re-introducing the legacy `ZITADEL_PORT` env-var Viper collision that motivated the prior `zitadel`→`zitadel-api` rename. Shared values live in `base/values.yaml`; each overlay layers env-specific diffs via `helmCharts.additionalValuesFiles`. The cross-directory `valuesFile: ../../base/values.yaml` reference requires `--load-restrictor=LoadRestrictionsNone` on both CI (`Makefile:lint-k8s`) and ArgoCD (`argocd-cm.kustomize.buildOptions`); the documented Kustomize trade-off (loss of kustomization relocatability) is acceptable here because no overlay is designed to be moved/copied.

#### Scenario: API Deployment originates from the chart

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** the output SHALL include a Deployment named `zitadel-api` whose `app.kubernetes.io/managed-by` label is `Helm`
- **AND** the Deployment SHALL run the image `ghcr.io/zitadel/zitadel:<pinned-tag>` at port `8080`

#### Scenario: Login UI Deployment originates from the chart

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** the output SHALL include a Deployment named `zitadel-api-login` whose `app.kubernetes.io/managed-by` label is `Helm`
- **AND** the Deployment SHALL run the image `ghcr.io/zitadel/zitadel-login:<pinned-tag>` at port `3000`

#### Scenario: Chart version is pinned

- **WHEN** the `helmCharts:` entry for `zitadel/zitadel-charts` is inspected in `kustomization.yaml`
- **THEN** the `version:` field SHALL be set to an explicit semver value (not `latest`)
- **AND** chart upgrades SHALL be performed by explicit edit to that field in a pull request

#### Scenario: HTTPRoute and HealthCheckPolicy reference chart-natural Service names

- **WHEN** the chart-rendered Services replace the hand-rolled Services
- **THEN** the `HTTPRoute` SHALL list backendRefs `zitadel-api` (API catch-all) and `zitadel-api-login` (Login UI path prefix `/ui/v2/login`)
- **AND** the `HealthCheckPolicy` resource `zitadel-api-policy` SHALL target the `zitadel-api` Service
- **AND** the `HealthCheckPolicy` resource `zitadel-web-policy` SHALL target the `zitadel-api-login` Service (the resource name `zitadel-web-policy` is retained for ops continuity; the targetRef is updated)

### Requirement: Login V2 UI Routes Outbound Calls Via Cluster-Internal Service Using CUSTOM_REQUEST_HEADERS

The Login UI container (chart-rendered Deployment `zitadel-api-login`) SHALL connect to the API via `ZITADEL_API_URL` pointed at the cluster-internal Service URL (`http://zitadel-api:80`, the chart's auto-generated default given `fullnameOverride: zitadel-api` and `service.port: 80`) AND SHALL carry the chart-auto-generated `CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>,X-Zitadel-Public-Host:<ExternalDomain>` so that Connect-RPC traffic stays in-cluster while presenting the public issuer hostname.

Because the API Service is HTTP/2 (`appProtocol: kubernetes.io/h2c`, `service.protocol: http2`), the on-the-wire `:authority` of a cluster-internal call equals the dial target `zitadel-api`; the `Host:<ExternalDomain>` custom header does NOT survive as `:authority` over h2c. Zitadel v4.7.1+ resolves the instance from `InstanceHostHeaders` (default `[x-zitadel-instance-host]`), NOT from the `Host` header, and the Login UI does not send `x-zitadel-instance-host`. Instance lookup therefore falls back to `:authority` = `zitadel-api`, which matches no `InstanceDomain` and fails with `Errors.Instance.NotFound`.

To resolve cluster-internal Login V2 calls to the correct virtual instance, the API config (`zitadel.configmapConfig`) SHALL set `InstanceHostHeaders` to include `x-zitadel-public-host` — the header the Login UI already sends with the public `<ExternalDomain>` value — ahead of or alongside the `x-zitadel-instance-host` default. The setting is domain-independent and SHALL live in the Helm base values so it applies to both environments. Browser→Gateway traffic, which sends neither `x-zitadel-instance-host` nor `x-zitadel-public-host`, SHALL remain unaffected and continue to resolve via the `:authority` fallback equal to `<ExternalDomain>`.

**Rationale**: Connecting to the cluster-internal Service keeps Login V2 traffic in-cluster and eliminates the prod GCP HTTPS LB hairpin that caused the original 30s timeout on `/ui/v2/login/login?authRequest=...`, replacing the prior `route-login-v2-via-internal-zitadel-api` apparatus (Pulumi Dynamic Resource + System User + GSM Secrets) with chart-delivered env values. However, the original assumption that the chart-generated `Host` + `X-Zitadel-Public-Host` pair is sufficient for instance resolution was incorrect for Zitadel v4.7.1+: a 504 incident on prod (`auth.liverty-music.app`, error ID `QUERY-1kIjX`, `instance_interceptor.go:100`, `instanceDomain zitadel-api, publicHostname auth.liverty-music.app`) showed instance lookup keying off `:authority` = `zitadel-api` over h2c rather than the `Host`/public-host header. Reusing the already-present `X-Zitadel-Public-Host` signal via `InstanceHostHeaders` fixes resolution with a single declarative key, no per-instance domain registration, no System User, and no setup re-run.

#### Scenario: Login UI Pod reaches the API via cluster-internal Service DNS

- **WHEN** the Login UI Pod (`zitadel-api-login`) issues an outbound Connect-RPC call
- **THEN** the connection target SHALL be the cluster-internal Service DNS name of the chart-rendered API Service (resolvable as `zitadel-api.zitadel.svc.cluster.local`)
- **AND** the request SHALL NOT egress to the GKE Gateway external IP

#### Scenario: API resolves the instance from the public-host header for internal calls

- **WHEN** the Zitadel API Pod receives a cluster-internal Login UI request whose `:authority` is `zitadel-api` and whose `X-Zitadel-Public-Host` header is the configured `<ExternalDomain>`
- **THEN** the API's `InstanceHostHeaders` SHALL include `x-zitadel-public-host`
- **AND** the `instance_interceptor` SHALL resolve the request to the virtual instance whose `InstanceDomain` equals `<ExternalDomain>`
- **AND** the API SHALL NOT log `unable to set instance` / `Errors.Instance.NotFound` for that call

#### Scenario: Browser traffic still resolves via the authority fallback

- **WHEN** a browser request arrives at the API through the GKE Gateway with `:authority` = `<ExternalDomain>` and no `x-zitadel-instance-host` or `x-zitadel-public-host` header
- **THEN** the `instance_interceptor` SHALL resolve the instance via the `:authority` fallback equal to `<ExternalDomain>`
- **AND** the resolution behavior SHALL be unchanged from before `InstanceHostHeaders` was set

#### Scenario: InstanceHostHeaders is set in the Helm base values

- **WHEN** the rendered `zitadel-api-config-yaml` ConfigMap is inspected in either environment
- **THEN** `InstanceHostHeaders` SHALL list `x-zitadel-public-host` (in addition to the `x-zitadel-instance-host` default)
- **AND** the setting SHALL originate from `k8s/namespaces/zitadel/base/values.yaml` (domain-independent, shared by dev and prod overlays)

#### Scenario: CUSTOM_REQUEST_HEADERS is auto-generated by the chart, not overridden

- **WHEN** the Login UI container env is inspected
- **THEN** the `CUSTOM_REQUEST_HEADERS` env var SHALL be sourced from the chart-rendered `login-config-dotenv` ConfigMap, which the chart auto-populates from `zitadel.configmapConfig.ExternalDomain` as `Host:<ExternalDomain>,X-Zitadel-Public-Host:<ExternalDomain>`
- **AND** `login.env` SHALL NOT carry a manual `CUSTOM_REQUEST_HEADERS` override (overriding inline drops the `X-Zitadel-Public-Host` half that the API's `InstanceHostHeaders` now reads for instance discovery from cluster-internal callers)
- **AND** there SHALL NOT be a Kustomize patch overriding `ZITADEL_API_URL` to a public hostname

#### Scenario: Interactive sign-in renders without a Gateway 504

- **WHEN** a user loads `https://auth.liverty-music.app/ui/v2/login/login?authRequest=...` after the change is deployed
- **THEN** the Gateway SHALL return a successful (non-5xx) response served by the Login UI SSR render
- **AND** the Login UI SHALL NOT log `Failed to fetch security settings from API`

### Requirement: Self-healing watchdog auto-restarts a wedged Zitadel API

The prod environment SHALL run an in-cluster watchdog that detects the Zitadel projection-trigger wedge (zitadel/zitadel#10103) and automatically restarts the `zitadel-api` Deployment without operator action. The watchdog SHALL be a Kubernetes `CronJob` modeled on the existing dev restart CronJob pattern (a container image carrying `curl` and `kubectl`, plus a dedicated ServiceAccount and a `Role`/`RoleBinding` scoped to `get`/`patch` on the `zitadel-api` Deployment in the `zitadel` namespace only) — NOT a compiled application.

The watchdog SHALL detect the wedge using an **auth-flow signal that exercises the wedged trigger-on-read path**, NOT a `/debug/healthz` or `/debug/ready` check (both return 200 during the wedge). The reference signal is an HTTP `GET` to `/oauth/v2/authorize` with **valid** OIDC parameters (a registered prod client id + redirect uri) that returns a `302` quickly when healthy and hangs past the gateway timeout when wedged. Invalid parameters SHALL NOT be used because they return `400` before the wedged code path and cannot detect the wedge.

The watchdog SHALL be **conservative against false restarts**:
- It SHALL restart only after **N consecutive hanging probes within a single run** (no single transient blip triggers a restart).
- It SHALL restart only when `/debug/healthz` returns `200` at probe time (the wedge signature is "core healthy AND auth-flow hung"); if core health is also failing it SHALL NOT restart, since the fault is not the wedge.
- It SHALL use `concurrencyPolicy: Forbid` so runs never overlap.

#### Scenario: Wedged pod is auto-restarted

- **WHEN** `/oauth/v2/authorize` (valid params) hangs past the gateway timeout for N consecutive probes in one run while `/debug/healthz` returns 200
- **THEN** the watchdog SHALL run the equivalent of `kubectl rollout restart deploy/zitadel-api` in the `zitadel` namespace
- **AND** a fresh `/oauth/v2/authorize` SHALL return `302` within normal latency after the new pod becomes Ready

#### Scenario: Transient blip does not trigger a restart

- **WHEN** a single probe in a run hangs but the remaining probes in the same run return `302`
- **THEN** the watchdog SHALL NOT restart the Deployment

#### Scenario: Full outage (core health down) does not trigger a restart

- **WHEN** the authorize probe fails AND `/debug/healthz` does not return 200 (e.g. gateway/DNS outage, pod not running)
- **THEN** the watchdog SHALL NOT restart the Deployment, because the fault is not the in-process wedge

#### Scenario: Healthy steady state issues no restart

- **WHEN** `/oauth/v2/authorize` returns `302` within normal latency on every probe
- **THEN** the watchdog SHALL take no action

