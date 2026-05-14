## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: First-Boot Org Looked Up via Provider Data Source

Pulumi SHALL NOT create the Zitadel "admin" org as a `zitadel.Org` resource for any environment where the org is auto-created by Zitadel's first-boot bootstrap (i.e., where `ZITADEL_FIRSTINSTANCE_ORG_NAME` is set in the deployment's configmap). Instead, Pulumi SHALL look up the existing org by name via the Zitadel provider's data source and reference its `id` for downstream resources such as the backend `MachineUser`.

**Rationale**: First-boot bootstrap creates the admin org outside Pulumi's state. Importing it as a Pulumi-managed resource creates a destroy-cascade hazard — `pulumi destroy` on the stack would attempt to delete the admin org, which is the same org the admin JWT belongs to, creating a circular dependency. Looking up the org as a data source (read-only) keeps Pulumi out of the org's lifecycle.

#### Scenario: Pulumi state has no `zitadel.Org` resource named "admin"

- **WHEN** the Pulumi stack is applied for an environment where first-boot bootstrap created the admin org (currently: prod)
- **THEN** Pulumi state SHALL NOT contain a `zitadel.Org` resource with name "admin"
- **AND** the backend `MachineUser` resource SHALL reference the org id resolved by a `zitadel.getOrg` (or equivalent) data source lookup

#### Scenario: Org lookup is unambiguous

- **WHEN** the data source `zitadel.getOrg({ name: 'admin' })` is invoked
- **THEN** it SHALL return exactly one org
- **AND** the component SHALL fail the Pulumi preview with a clear error message if the lookup returns zero or multiple results

### Requirement: Prod Backend MachineKey Component Authenticates with Bootstrap-Uploaded Admin JWT

The Pulumi `BackendMachineKeyComponent` (or equivalent top-level component) for the prod stack SHALL configure its Zitadel provider with `domain: 'auth.liverty-music.app'` and the `jwtProfileJson` SHALL be sourced from the GSM SecretVersion `zitadel-machine-key-for-pulumi-admin` (project `liverty-music-prod`) via a `gcp.secretmanager.getSecretVersion` data source — NOT from a Pulumi config or ESC value. The component SHALL fail Pulumi preview/up with a clear error if the GSM Secret has zero enabled versions.

**Rationale**: The org-admin JWT is minted by Zitadel's first-boot bootstrap and uploaded to GSM by the in-cluster `bootstrap-uploader` sidecar — it is generated *after* Pulumi creates the GSM Secret shell, so it cannot be a Pulumi-config input at stack-create time. Reading it via a data source on each `pulumi up` ensures Pulumi always uses the current version and preserves the source-of-truth ordering (Zitadel → GSM → Pulumi-runtime, never Pulumi → JWT).

#### Scenario: Provider configured from GSM data source

- **WHEN** the prod Pulumi stack is applied
- **THEN** the Zitadel provider's `jwtProfileJson` argument SHALL be a Pulumi `Output<string>` produced by a `gcp.secretmanager.getSecretVersion` data source pointing at the GSM Secret `zitadel-machine-key-for-pulumi-admin` in project `liverty-music-prod`
- **AND** the JWT value SHALL NOT appear in the Pulumi stack's config nor in any ESC environment

#### Scenario: Missing GSM secret fails fast

- **WHEN** the prod Pulumi stack is applied and the GSM Secret `zitadel-machine-key-for-pulumi-admin` has zero enabled versions
- **THEN** Pulumi preview SHALL fail with a clear "secret version not found" error referencing the missing GSM resource
- **AND** no Zitadel MachineUser, MachineKey, or downstream GSM resource SHALL be created
