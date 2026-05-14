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

### Requirement: Backend MachineUser Placed in Product Org, Not the First-Boot Admin Org

The Pulumi `BackendMachineKeyComponent` (or equivalent) SHALL create the backend `MachineUser` (with its `ORG_USER_MANAGER` role grant) inside a **Pulumi-managed product org** (named `liverty-music`), NOT the first-boot "admin" org. Pulumi SHALL NOT create or manage the first-boot admin org (which the Zitadel runtime auto-creates via `ZITADEL_FIRSTINSTANCE_ORG_NAME`); attempting to own it would create a destroy-cascade hazard because the org-admin JWT used by Pulumi's Zitadel provider belongs to that org.

**Rationale**: The first-boot admin org holds operator identities — `pulumi-admin` (IaC break-glass), `login-client` (Login V2 PAT host), and any human IAM_OWNER admins. Granting the backend MachineUser `ORG_USER_MANAGER` in that org would let the runtime backend Pod create, suspend, or modify those operator identities — a privilege-escalation foothold from a compromised backend Pod to the IaC/admin tier. Placing backend-app in a separate Pulumi-managed product org confines `ORG_USER_MANAGER` to end-user principals (per the `Place Machine Users by Responsibility` rule that the dev path already implements via `productOrg`).

#### Scenario: backend-app MachineUser lives in the product org

- **WHEN** the Pulumi stack is applied
- **THEN** Pulumi state SHALL contain a `zitadel.Org` resource with name `liverty-music` (the product org)
- **AND** the backend `MachineUser` resource SHALL reference `productOrg.id` (NOT the first-boot admin org id)
- **AND** the `OrgMember` resource granting `ORG_USER_MANAGER` SHALL also scope to `productOrg.id`

#### Scenario: Pulumi does not manage the first-boot admin org

- **WHEN** Pulumi state is exported
- **THEN** it SHALL NOT contain any `zitadel.Org` resource that targets the org auto-created by `ZITADEL_FIRSTINSTANCE_ORG_NAME` (typically named `admin`)
- **AND** no data-source lookup against the admin org SHALL be required for this component (the provider's JWT identity is already scoped to the admin org for org-creation authority; the resolved-org name is irrelevant to downstream operations because backend resources live in `productOrg`)

### Requirement: Prod Backend MachineKey Component Authenticates with Bootstrap-Uploaded Admin JWT

The Pulumi `BackendMachineKeyComponent` (or equivalent top-level component) for the prod stack SHALL configure its Zitadel provider with `domain: 'auth.liverty-music.app'` and the `jwtProfileJson` SHALL be sourced from the GSM SecretVersion `zitadel-machine-key-for-pulumi-admin` (project `liverty-music-prod`) via a `gcp.secretmanager.getSecretVersionAccess` data source — NOT from a Pulumi config or ESC value. The fetched secret value SHALL be wrapped in `pulumi.secret()` before being passed to the provider so that the embedded RSA private key never appears in plaintext in `pulumi preview` output, CI logs, or Pulumi state history.

**Rationale**: The org-admin JWT is minted by Zitadel's first-boot bootstrap and uploaded to GSM by the in-cluster `bootstrap-uploader` sidecar — it is generated *after* Pulumi creates the GSM Secret shell, so it cannot be a Pulumi-config input at stack-create time. Reading it via a data source on each `pulumi up` ensures Pulumi always uses the current version and preserves the source-of-truth ordering (Zitadel → GSM → Pulumi-runtime, never Pulumi → JWT). The `pulumi.secret()` wrap is required because `getSecretVersionAccessOutput` does NOT auto-mark its output as secret; without it, the JWT-profile JSON (which embeds an RSA private key) would surface in plaintext in `pulumi preview` diffs and Pulumi service state history. The same wrap MUST also be applied when persisting the produced backend `MachineKey.keyDetails` into the `zitadel-machine-key-for-backend-app` SecretVersion (the `@pulumiverse/zitadel` provider similarly does not auto-mark `keyDetails` as secret).

#### Scenario: Provider configured from GSM data source

- **WHEN** the prod Pulumi stack is applied
- **THEN** the Zitadel provider's `jwtProfileJson` argument SHALL be a Pulumi `Output<string>` produced by a `gcp.secretmanager.getSecretVersionAccess` data source pointing at the GSM Secret `zitadel-machine-key-for-pulumi-admin` in project `liverty-music-prod`
- **AND** the value SHALL be wrapped in `pulumi.secret()` before being passed to the provider
- **AND** the JWT value SHALL NOT appear in the Pulumi stack's config nor in any ESC environment

#### Scenario: Missing GSM secret fails fast

- **WHEN** the prod Pulumi stack is applied and the GSM Secret `zitadel-machine-key-for-pulumi-admin` has zero enabled versions
- **THEN** Pulumi preview SHALL fail with a clear "secret version not found" error referencing the missing GSM resource
- **AND** no Zitadel MachineUser, MachineKey, or downstream GSM resource SHALL be created

#### Scenario: Backend MachineKey JWT is secret-wrapped before write

- **WHEN** the `BackendMachineKeyComponent` writes the produced `MachineKey.keyDetails` to the `gcp.secretmanager.SecretVersion` for `zitadel-machine-key-for-backend-app`
- **THEN** the `secretData` argument SHALL be wrapped in `pulumi.secret()` so the JWT-profile JSON does not appear in plaintext in Pulumi state history
