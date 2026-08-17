## MODIFIED Requirements

### Requirement: Backend MachineKey Lifecycle Tied to Zitadel-Side Identity

The fan-facing API's Zitadel MachineKey SHALL be stored in a GSM secret named
`zitadel-machine-key-for-fan-api`, following the platform-wide convention
`zitadel-machine-key-for-<principal>` where `<principal>` is the workload name from
the `workload-naming-convention` capability. The `fan-api` principal is the renamed
`backend-app` workload (see `workload-naming-convention`); the legacy GSM name
`zitadel-machine-key-for-backend-app` (itself a prior rename from the ambiguous
`zitadel-machine-key`) SHALL be migrated to the new principal name via the additive
create-new → cutover → delete-old sequence, re-issuing the MachineKey so the GSM
`keyDetails` and the Zitadel AuthNKey stay consistent across the rename.

The name encodes which Zitadel principal owns the key so the platform's multiple
`MachineKey`s (`pulumi-admin`, `fan-api`) remain distinguishable at a glance — the
ambiguity of the original `zitadel-machine-key` directly cost triage time in the
§13.15 incident chain.

#### Scenario: keyId in GSM matches Zitadel DB

- **WHEN** Pulumi state contains a `MachineKey` for a given user
- **THEN** the `keyId` in the GSM SecretVersion's JSON SHALL match a row in Zitadel's AuthNKey table for that user
- **AND** the fan-api → Zitadel API JWT bearer auth SHALL succeed

#### Scenario: Force-replace on detected drift

- **WHEN** the operator detects keyId drift (e.g., via `Errors.AuthNKey.NotFound` in fan-api logs)
- **THEN** the operator SHALL force-replace the Pulumi `MachineKey` resource by changing a non-cosmetic property (e.g., bumping `expirationDate` to a different valid value)
- **AND** the resulting Pulumi apply SHALL produce a new `keyDetails` value, propagate it through the dependency graph, replace the GSM SecretVersion, sync ESO, and trigger Reloader-driven fan-api Pod restart

#### Scenario: Both dev and prod produce a Backend MachineKey

- **WHEN** `pulumi up` runs for the `dev` stack and again for the `prod` stack
- **THEN** each stack's resulting Pulumi state SHALL contain exactly one `MachineKey` resource for the `fan-api` machine user
- **AND** each stack's GSM project (`liverty-music-dev` and `liverty-music-prod` respectively) SHALL contain a Secret named `zitadel-machine-key-for-fan-api` with at least one enabled SecretVersion

#### Scenario: The legacy backend-app key name is retired after migration

- **WHEN** the rename migration has completed in an environment
- **THEN** no GSM secret named `zitadel-machine-key-for-backend-app` SHALL remain, and the fan-api workload SHALL read only `zitadel-machine-key-for-fan-api`
