# secret-management Specification

## Purpose

Defines how runtime secrets are securely stored in GCP Secret Manager and delivered to backend pods as environment variables via External Secrets Operator (ESO), without application code changes.

## Requirements

### Requirement: GCP Secret Manager provisioning

The infrastructure SHALL provision GCP Secret Manager secrets via Pulumi (inline in `KubernetesComponent`) for each runtime secret required by backend workloads. Each secret MUST be created in the environment-specific GCP project. Secret names use kebab-case without an environment prefix (e.g., `lastfm-api-key`); environment isolation is provided by the GCP project itself.

> **Note**: GCP Secret Manager does not support `/` in secret names. Environment isolation comes from the project boundary (`liverty-music-dev` vs `liverty-music-prod`), not the name.

#### Scenario: LASTFM_API_KEY secret creation

- **WHEN** the Pulumi dev stack is applied
- **THEN** a GCP Secret Manager secret named `lastfm-api-key` is created in the `liverty-music-dev` project

#### Scenario: Secret version provisioning

- **WHEN** a secret resource exists in GCP Secret Manager
- **THEN** a secret version SHALL be created with the actual secret value
- **AND** the secret value MUST NOT appear in Pulumi state in plaintext (use `pulumi.requireSecret()`)
- **AND** the secret value SHALL be read from Pulumi ESC config key `gcp.lastFmApiKey`

### Requirement: IAM access control for secrets

The `backend-app` GCP service account SHALL be granted `roles/secretmanager.secretAccessor` on secret resources it needs to access. No other service accounts SHALL have access unless explicitly provisioned.

#### Scenario: Backend service account secret access

- **WHEN** the backend-app pod authenticates via Workload Identity
- **THEN** it can read secret versions from GCP Secret Manager for secrets in its environment project

#### Scenario: Least privilege enforcement

- **WHEN** a service account without `secretmanager.secretAccessor` role attempts to read a secret
- **THEN** the request is denied

### Requirement: External Secrets Operator deployment

The cluster SHALL run External Secrets Operator (ESO) as a managed component deployed via ArgoCD.

ESO authenticates to GCP Secret Manager using Pod Identity (Application Default Credentials): the ESO controller's K8s service account (`external-secrets/external-secrets`) is annotated with a dedicated GCP service account (`k8s-external-secrets`) via Workload Identity Federation. No static credentials or `auth` section in the ClusterSecretStore are required.

#### Scenario: ESO controller availability

- **WHEN** listing pods in the `external-secrets` namespace
- **THEN** the ESO controller pod is running and healthy

#### Scenario: ESO CRDs installed

- **WHEN** listing Custom Resource Definitions
- **THEN** `externalsecrets.external-secrets.io`, `secretstores.external-secrets.io`, and `clustersecretstores.external-secrets.io` CRDs are present

### Requirement: ClusterSecretStore configuration

The cluster SHALL have a `ClusterSecretStore` resource that connects to GCP Secret Manager using Workload Identity authentication (Pod Identity / ADC). The store SHALL restrict access to the `backend` namespace via `spec.conditions.namespaces`.

#### Scenario: ClusterSecretStore creation

- **WHEN** the backend Kustomize manifests are applied
- **THEN** a `ClusterSecretStore` named `google-secret-manager` exists
- **AND** it references the environment's GCP project ID
- **AND** it uses Workload Identity for authentication (no static credentials, no `clusterLocation`/`clusterName` fields)
- **AND** `spec.conditions.namespaces` restricts ExternalSecret submissions to the `backend` namespace

#### Scenario: ClusterSecretStore health

- **WHEN** inspecting the ClusterSecretStore status
- **THEN** the `Ready` condition is `True`

### Requirement: ExternalSecret for backend secrets

An `ExternalSecret` resource SHALL exist in the backend namespace that maps GCP Secret Manager secrets to a K8s Secret with environment variable keys matching `config.go` expectations.

#### Scenario: ExternalSecret syncs LASTFM_API_KEY

- **WHEN** the ExternalSecret is reconciled
- **THEN** a K8s Secret named `backend-secrets` is created in the backend namespace
- **AND** it contains a key `LASTFM_API_KEY` with the value from GCP Secret Manager secret `lastfm-api-key`

#### Scenario: ExternalSecret refresh interval

- **WHEN** a secret value is updated in GCP Secret Manager
- **THEN** the ExternalSecret controller detects the change within the configured `refreshInterval`
- **AND** the K8s Secret is updated with the new value

#### Scenario: Adding a new secret

- **WHEN** a new key-value pair is added to the ExternalSecret `data` array
- **AND** the corresponding GCP Secret Manager secret exists
- **THEN** the new key appears in the `backend-secrets` K8s Secret without application code changes

### Requirement: Backend Deployment secret consumption

The backend Deployment SHALL consume secrets from the K8s Secret via `envFrom: secretRef`, alongside the existing ConfigMap.

#### Scenario: Pod receives secret as environment variable

- **WHEN** a backend pod starts
- **THEN** the `LASTFM_API_KEY` environment variable is populated from the `backend-secrets` K8s Secret
- **AND** the application reads it via `os.Getenv("LASTFM_API_KEY")` without code changes

#### Scenario: Pod startup failure on missing secret

- **WHEN** the `backend-secrets` K8s Secret does not exist
- **THEN** the pod fails to start with a clear error indicating the missing secret reference

### Requirement: Postmark Server API Token in Pulumi ESC

The Postmark Server API Token SHALL be stored in Pulumi ESC at the environment level (not common) under `pulumiConfig.postmark.serverApiToken` as a secret. Postmark uses the same token as both the SMTP username and password, so a single config field is sufficient.

**Rationale**: Zitadel Cloud connects to Postmark SMTP directly, not via K8s pods. The token does not need to be provisioned in GCP Secret Manager or delivered via ESO. Pulumi ESC is the correct store for infrastructure-only secrets consumed during `pulumi up`.

#### Scenario: Setting dev Postmark token

- **WHEN** configuring the dev environment
- **THEN** `esc env set liverty-music/dev pulumiConfig.postmark.serverApiToken "<value>" --secret` stores the Postmark Server API Token as encrypted

#### Scenario: Setting prod Postmark token

- **WHEN** configuring the prod environment
- **THEN** `esc env set liverty-music/prod pulumiConfig.postmark.serverApiToken "<value>" --secret` stores the Postmark Server API Token as encrypted

#### Scenario: Credentials are not in GCP Secret Manager

- **WHEN** the Postmark Server API Token is needed
- **THEN** it SHALL be consumed directly by Pulumi via ESC config
- **AND** it SHALL NOT be provisioned as a GCP Secret Manager secret (Zitadel Cloud connects to SMTP directly, not via K8s pods)

### Requirement: Secret rotation propagation

Secret updates in GCP Secret Manager SHALL propagate to running backend pods via automatic Deployment rolling restart.

#### Scenario: Rotation triggers pod restart

- **WHEN** a secret value is updated in GCP Secret Manager
- **AND** the ExternalSecret controller syncs the new value to the K8s Secret
- **THEN** Reloader detects the Secret change
- **AND** triggers a rolling restart of the backend Deployment
- **AND** new pods start with the updated secret value

#### Scenario: Zero-downtime rotation

- **WHEN** a rolling restart is triggered by secret rotation
- **THEN** the Deployment maintains availability with `maxUnavailable: 0`
