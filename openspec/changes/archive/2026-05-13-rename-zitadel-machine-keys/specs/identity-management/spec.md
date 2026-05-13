## MODIFIED Requirements

### Requirement: Retain Break-glass Machine User

The system SHALL retain the `pulumi-admin` machine user with `IAM_OWNER`
membership and its JSON key in GCP Secret Manager (`zitadel-machine-key-for-pulumi-admin`)
as a break-glass identity that does not depend on Google sign-in being
operational. This requirement protects against total Console lockout if
the Google IdP, OAuth client, or human admin user is misconfigured or
removed.

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

#### Scenario: Break-glass identity exists

- **WHEN** Pulumi stack is applied
- **THEN** the `pulumi-admin` machine user SHALL exist in the `admin` role
  org with `IAM_OWNER`
- **AND** its JSON key SHALL be present in GCP Secret Manager as
  `zitadel-machine-key-for-pulumi-admin`
- **AND** neither the user nor its key SHALL be deleted, replaced, or
  rotated as a side effect of provisioning the human admin user, IdP, or
  login policy
- **AND** the only legitimate write to `zitadel-machine-key-for-pulumi-admin` SHALL be
  performed by the in-cluster `bootstrap-uploader` sidecar at
  first-instance bootstrap (idempotent)

#### Scenario: Recover from broken Google sign-in

- **WHEN** the human admin user cannot sign in via Google (IdP outage,
  misconfigured OAuth client, accidentally deleted human user, etc.)
- **THEN** an operator SHALL be able to authenticate the Pulumi
  `@pulumiverse/zitadel` provider with the `zitadel-machine-key-for-pulumi-admin` JSON key
- **AND** run Pulumi to restore the human admin user, IdP, or login
  policy
- **AND** Console access via Google SHALL resume after the next Pulumi
  apply
