## REMOVED Requirements

### Requirement: Backend MachineUser Placed in Product Org, Not the First-Boot Admin Org

**Reason**: Superseded by the new general-form requirement "Backend MachineUser Lives in Product Org Across All Environments" (ADDED above). The removed requirement was written in `enable-zitadel-prod-pulumi-provider` with prod-specific language ("Pulumi `BackendMachineKeyComponent` (or equivalent) SHALL ...") that constrained the implementation choice to a parallel wrapper class. The new general-form requirement applies env-agnostically and does not constrain the implementation to a particular wrapper.

**Migration**: Implementations satisfying the removed requirement automatically satisfy the new general-form requirement, as the rule itself (product-org placement of backend `MachineUser` + ORG_USER_MANAGER) is preserved. The constraint that was relaxed is the implementation shape: the unified `Zitadel` class replaces the prod-specific `BackendMachineKeyComponent` while continuing to honor the org-placement rule.

### Requirement: Prod Backend MachineKey Component Authenticates with Bootstrap-Uploaded Admin JWT

**Reason**: The `BackendMachineKeyComponent` (the subject of this requirement) is deleted by this change. Its responsibilities — fetching the admin JWT from GSM via `getSecretVersionAccessOutput`, wrapping it in `pulumi.secret()`, configuring the `zitadel.Provider` — are absorbed into the unified `Zitadel` class and apply to all envs uniformly. The new ADDED requirement "Backend MachineUser Lives in Product Org Across All Environments" scenarios `Admin org imported via inline import: resource option, env-keyed id` and `Provider sourced from GSM admin JWT in all envs` together cover all the operational invariants the removed requirement encoded.

**Migration**: The `pulumi.secret()` wrap, the GSM data source, and the failure-on-missing-version behavior are all preserved in the unified `Zitadel` class. Implementations migrating from `BackendMachineKeyComponent` SHALL:
1. Delete the `BackendMachineKeyComponent` file.
2. Remove the `env !== 'dev'` throw guard from the `Zitadel` class.
3. Source the admin JWT inside the unified class (it was already there pre-refactor for dev; remove the env guard so the same code path runs in prod).
4. Accept the prod state migration cost: the previous `BackendMachineKey$...` URNs are destroyed and recreated under `Zitadel$...` URNs on the first prod `pulumi up`. Brief backend-auth outage (~2-5 min pre-launch).

## MODIFIED Requirements

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
