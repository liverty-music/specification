## MODIFIED Requirements

### Requirement: Bootstrap Admin Machine Key Stored in Secret Manager

On first startup of an empty database, Zitadel SHALL create an initial admin machine user by consuming `ZITADEL_FIRSTINSTANCE_*` environment variables, write the resulting JWT-profile JSON key to a shared `emptyDir` pod volume, and a `bootstrap-uploader` sidecar container co-located in the same Zitadel API Pod SHALL upload that key to GCP Secret Manager as `zitadel-machine-key-for-pulumi-admin`; subsequent Pulumi stack applies SHALL read the key from Secret Manager as the `jwtProfileJson` for the Zitadel provider.

**Rationale**: This closes the bootstrap chicken-and-egg — Pulumi needs admin credentials to configure Zitadel, but admin credentials only exist after Zitadel has bootstrapped itself. Shifting the boundary into the cluster avoids manual human steps. A separate Kubernetes `Job` cannot share an `emptyDir` volume with the Zitadel Deployment Pod (volumes are Pod-scoped), so the uploader runs as a sidecar container inside the Zitadel API Pod where the shared volume is naturally accessible. The sidecar idles after the upload (`tail -f /dev/null`) so the Pod stays ready and the upload is idempotent across Pod restarts (it skips re-uploading when the stored GSM version already matches).

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`, where `<principal>` is the Pulumi `MachineUser` resource id. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

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

### Requirement: Backend MachineKey Lifecycle Tied to Zitadel-Side Identity

The backend's machine-user JWT private key (`zitadel-machine-key-for-backend-app` in GSM) SHALL track the `MachineKey` Pulumi resource's `keyDetails` output one-to-one. State drift between the Zitadel DB, the GSM SecretVersion, and the Pulumi state SHALL be treated as a critical incident — backend → Zitadel API auth fails with `Errors.AuthNKey.NotFound` whenever the kid in the GSM-mounted JSON key does not have a matching row in Zitadel's AuthNKey table.

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
- **AND** the resulting Pulumi apply SHALL produce a new `keyDetails` value, propagate it through `KubernetesComponent.secrets`, replace the GSM SecretVersion, sync ESO, and trigger Reloader-driven backend Pod restart

## ADDED Requirements

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
