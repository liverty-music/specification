## MODIFIED Requirements

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password reset emails, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the API call to send the email returns success (202-equivalent), the notification worker logs nothing, and the user-facing UX is "no email arrived." Discovered during the dev cutover smoke test when sign-up succeeded but verification emails never reached Postmark. The original requirement said "Pulumi Dynamic Resource OR equivalent"; this modification removes the "OR equivalent" escape and pins the contract to the Dynamic Resource so a manual `curl` step cannot be a "valid implementation" — every Zitadel rebuild must activate SMTP declaratively without operator memory.

#### Scenario: Newly provisioned SMTP config is activated automatically

- **WHEN** Pulumi provisions a `SmtpConfig` resource on a fresh Zitadel instance
- **THEN** the `ZitadelSmtpActivation` Dynamic Resource SHALL call `POST /admin/v1/smtp/{id}/_activate` as part of the same `pulumi up`
- **AND** the resulting state SHALL be `SMTP_CONFIG_ACTIVE`
- **AND** subsequent verification emails SHALL be queued AND delivered to the SMTP provider

#### Scenario: Activation is idempotent across re-apply

- **WHEN** Pulumi re-applies the stack and the SMTP config is already active
- **THEN** the `ZitadelSmtpActivation` resource's `update` handler SHALL be a no-op AND SHALL NOT fail
- **AND** SHALL NOT trigger a destructive replace
- **AND** the Pulumi state graph SHALL continue to record the resource as up-to-date

#### Scenario: Activation runs on a fresh Zitadel rebuild without operator intervention

- **WHEN** the dev (or future staging / prod) Zitadel instance is destroyed and recreated from scratch
- **AND** Pulumi runs `pulumi up` against the recreated instance
- **THEN** the `SmtpConfig` resource SHALL be recreated
- **AND** the `ZitadelSmtpActivation` resource SHALL fire `_activate` automatically as the next step in the dependency graph
- **AND** the operator SHALL NOT need to run any manual `curl` or `gcloud` step
- **AND** the first user sign-up after the rebuild SHALL receive a verification email
