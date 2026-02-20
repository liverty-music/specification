## Context

Runtime secrets for the backend are currently unmanaged. The backend reads `LASTFM_API_KEY` (and will read future API keys) via `os.Getenv()`, but there is no K8s Secret backing these values. All environment variables are served from a single ConfigMap, mixing sensitive and non-sensitive data.

The infrastructure already uses:
- **GKE Autopilot** (asia-northeast2) with Workload Identity
- **Kustomize** base/overlay pattern for K8s manifests
- **ArgoCD** for GitOps-based continuous delivery
- **Pulumi** for GCP resource provisioning with ESC for IaC-time secrets
- **IAM-based authentication** for Cloud SQL (no password management)

The gap is a runtime secret delivery pipeline: GCP Secret Manager → K8s Pod environment variables.

## Goals / Non-Goals

**Goals:**
- Securely store and deliver runtime secrets (starting with `LASTFM_API_KEY`) to backend pods
- Zero application code changes -- secrets consumed as environment variables via `os.Getenv()`
- GitOps-compatible -- all K8s resources declarative in Kustomize manifests
- Extensible pattern -- adding a new secret requires only GCP SM entry + ExternalSecret key addition
- Rotation-ready -- secret updates in GCP SM propagate to pods automatically

**Non-Goals:**
- Application-level secret caching or hot-reload (Pod restart on rotation is acceptable)
- Secrets for frontend or other non-backend workloads (future scope)
- Migrating Pulumi ESC secrets to GCP Secret Manager (ESC remains for IaC-time config)
- Secret generation or automated rotation scheduling in GCP (manual secret value management for now)

## Decisions

### Decision 1: External Secrets Operator (ESO) over GCP Secret Manager CSI Driver

**Choice**: ESO

**Rationale**:
- ESO creates native K8s Secrets, consumed via `envFrom: secretRef` -- identical to existing ConfigMap pattern. No `config.go` changes needed.
- CSI Driver mounts secrets as files, requiring either application changes or `syncSecret` workaround (adds complexity for the same result).
- ESO provides clear error reporting via `ExternalSecret` status conditions. CSI Driver failures manifest as opaque Pod scheduling errors.
- ESO is a CNCF Sandbox project with broad community support and multi-provider capability.
- CSI Driver's only advantage (native GKE addon) is offset by ESO's straightforward Helm-based deployment under ArgoCD.

**Alternatives considered**:
- **CSI Driver**: Native GKE addon but requires file-based consumption or complex syncSecret configuration.
- **Init Container (custom)**: Maximum flexibility but high maintenance cost and no standard rotation support.
- **Pulumi ESC runtime integration**: ESC is designed for build/deploy time, not K8s pod runtime injection.

### Decision 2: ESO deployed via ArgoCD Helm Application

**Choice**: Manage ESO as an ArgoCD Application pointing to the ESO Helm chart.

**Rationale**:
- Consistent with existing ArgoCD-based GitOps workflow.
- ESO controller runs in a dedicated namespace (e.g., `external-secrets`), separate from application workloads.
- ArgoCD handles upgrades and drift detection for the operator itself.
- Avoids Pulumi managing in-cluster operators (keeps Pulumi focused on GCP resources).

### Decision 3: ClusterSecretStore scoped per environment

**Choice**: One `ClusterSecretStore` per cluster (each cluster is single-environment), referencing the environment's GCP project via Workload Identity.

**Rationale**:
- GKE clusters are already environment-specific (`liverty-music-dev`, `liverty-music-prod`).
- `ClusterSecretStore` avoids per-namespace SecretStore duplication.
- Authentication uses existing Workload Identity binding -- the `backend-app` GCP SA gets `roles/secretmanager.secretAccessor`.

### Decision 4: Secret naming convention in GCP Secret Manager

**Choice**: Flat kebab-case name (e.g., `lastfm-api-key`). No environment prefix.

**Rationale**:
- GCP Secret Manager does not support `/` in secret IDs (only letters, numbers, hyphens, underscores are allowed). The original `{env}/{secret-name}` design was infeasible.
- Environment isolation is provided by the GCP project boundary (`liverty-music-dev` vs `liverty-music-prod`). A per-environment prefix in the name is redundant.
- Kebab-case secret names align with existing resource naming conventions.
- Maps cleanly to ExternalSecret `remoteRef.key` field.
- Secret value is sourced from Pulumi ESC config key `gcp.lastFmApiKey` (set with `--secret`).

### Decision 5: Rotation via Reloader

**Choice**: Deploy [Stakater Reloader](https://github.com/stakater/Reloader) to trigger rolling restarts when K8s Secrets change.

**Rationale**:
- Environment variables are only read at process startup; K8s Secret updates alone do not propagate to running pods.
- Reloader watches for Secret changes and triggers Deployment rolling updates.
- Annotation-based (`reloader.stakater.com/auto: "true"`) -- minimal manifest change.
- Well-established pattern in the K8s ecosystem, lightweight DaemonSet.

## Risks / Trade-offs

- **[ESO operator availability]** → ESO controller downtime prevents secret sync. Mitigation: K8s Secrets persist independently; existing pods continue running. New pods may fail if Secret doesn't exist yet. ESO supports HA mode with multiple replicas.

- **[Secret sync latency]** → ExternalSecret `refreshInterval` introduces delay between GCP SM update and K8s Secret update. Mitigation: Set reasonable interval (e.g., 1h for API keys). Manual `kubectl annotate externalsecret --overwrite` forces immediate refresh.

- **[Reloader restart impact]** → Secret rotation triggers pod restarts, causing brief availability dip. Mitigation: Rolling update strategy with `maxUnavailable: 0` ensures zero-downtime rotation. API keys rotate infrequently (months/years).

- **[Additional cluster components]** → ESO + Reloader add operational surface. Mitigation: Both are mature, well-maintained projects. Deployed via ArgoCD for consistent management. Can be removed if GKE natively supports env-var secret injection in the future.

- **[etcd secret storage]** → K8s Secrets stored in etcd. Mitigation: GKE encrypts etcd at rest by default. For additional protection, GKE supports customer-managed encryption keys (CMEK) -- out of scope for now.
