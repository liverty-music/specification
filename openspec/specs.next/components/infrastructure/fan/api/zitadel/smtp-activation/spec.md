# Smtp Activation

## Purpose

Manage identity, authentication, and authorization policies for the Liverty Music platform.

## Requirements

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag. The activation SHALL additionally be **self-healing**: the resource's `read` handler SHALL query the live SMTP config's activation state, so that a runtime loss of activation (an instance rebuild/reset, or an out-of-band deactivation, that does not change the resource's Pulumi inputs) is surfaced as drift and re-activated on the next refreshing `pulumi up`, without an input change or a manual step.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password-reset emails, passkey-registration links, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the send API returns success, the notification worker logs nothing, and the user-facing UX is "no email arrived." The original implementation activated once at create time but treated every later reconcile as a no-op (no `read`, no re-check), so once the live activation drifted the outage was permanent and undetectable. This was observed in prod: `SendPasswordlessRegistration` succeeded yet Postmark received zero sends. The contract is therefore strengthened from "activate once" to "activate and keep active."

#### Scenario: Newly provisioned SMTP config is activated automatically

- **WHEN** Pulumi provisions a `SmtpConfig` resource on a fresh Zitadel instance
- **THEN** the `ZitadelSmtpActivation` Dynamic Resource SHALL call `POST /admin/v1/smtp/{id}/_activate` as part of the same `pulumi up`
- **AND** the resulting state SHALL be `SMTP_CONFIG_ACTIVE`
- **AND** subsequent verification emails SHALL be queued AND delivered to the SMTP provider

#### Scenario: First apply against an already-active SMTP succeeds (create-time idempotency)

- **WHEN** Pulumi runs `create()` for `ZitadelSmtpActivation` against an SMTP config that is already in `SMTP_CONFIG_ACTIVE` state (e.g., activated out-of-band prior to this resource being added to the stack)
- **THEN** the `_activate` POST SHALL return Zitadel's "already active" response shape
- **AND** `create()` SHALL treat that response as success
- **AND** the resource SHALL be recorded in Pulumi state with a fresh `activatedAt` timestamp

#### Scenario: Refresh detects a drifted (inactive) SMTP and re-activation heals it

- **WHEN** the live SMTP config has drifted to a non-active state (e.g., after an instance rebuild/reset or an out-of-band deactivation) while the `ZitadelSmtpActivation` resource's Pulumi inputs are unchanged
- **AND** an operator runs a refreshing `pulumi up` (`pulumi up --refresh`, or a stack whose deployment refreshes)
- **THEN** the `read` handler SHALL query the live activation state and report the resource as out-of-date (drifted)
- **AND** the ensuing `pulumi up` SHALL re-invoke `_activate` so the config returns to `SMTP_CONFIG_ACTIVE`
- **AND** no manual `curl`/`gcloud` step and no input change SHALL be required to heal it

#### Scenario: Re-apply with unchanged inputs is a Pulumi-graph no-op

- **WHEN** Pulumi re-applies the stack **without a refresh** and the `ZitadelSmtpActivation` resource's inputs (`smtpConfigId`, `domain`, `jwtProfileJson`) are unchanged from the previous apply
- **THEN** Pulumi's input diff SHALL be empty
- **AND** no lifecycle handler (`create` / `update` / `delete` / `read`) on `ZitadelSmtpActivation` SHALL be invoked (drift detection is the refreshing-apply path above)
- **AND** zero HTTP traffic SHALL be generated against the Zitadel admin API
- **AND** the Pulumi state graph SHALL continue to record the resource as up-to-date

#### Scenario: Activation runs on a fresh Zitadel rebuild without operator intervention

- **WHEN** the dev (or staging / prod) Zitadel instance is destroyed and recreated from scratch
- **AND** Pulumi runs `pulumi up` against the recreated instance
- **THEN** the `SmtpConfig` resource SHALL be recreated
- **AND** the `ZitadelSmtpActivation` resource SHALL fire `_activate` automatically as the next step in the dependency graph
- **AND** the operator SHALL NOT need to run any manual `curl` or `gcloud` step
- **AND** the first user sign-up after the rebuild SHALL receive a verification email
