## ADDED Requirements

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password reset emails, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the API call to send the email returns success (202-equivalent), the notification worker logs nothing, and the user-facing UX is "no email arrived." Discovered during the dev cutover smoke test when sign-up succeeded but verification emails never reached Postmark. The implementation contract is pinned to the Dynamic Resource (rather than "Dynamic Resource OR equivalent") so a manual `curl` step cannot be a "valid implementation" — every Zitadel rebuild must activate SMTP declaratively without operator memory.

#### Scenario: Newly provisioned SMTP config is activated automatically

- **WHEN** Pulumi provisions a `SmtpConfig` resource on a fresh Zitadel instance
- **THEN** the `ZitadelSmtpActivation` Dynamic Resource SHALL call `POST /admin/v1/smtp/{id}/_activate` as part of the same `pulumi up`
- **AND** the resulting state SHALL be `SMTP_CONFIG_ACTIVE`
- **AND** subsequent verification emails SHALL be queued AND delivered to the SMTP provider

#### Scenario: First apply against an already-active SMTP succeeds (create-time idempotency)

- **WHEN** Pulumi runs `create()` for `ZitadelSmtpActivation` against an SMTP config that is already in `SMTP_CONFIG_ACTIVE` state (e.g., activated out-of-band by a manual `curl` step prior to this resource being added to the stack)
- **THEN** the `_activate` POST SHALL return Zitadel's "already active" response shape
- **AND** `create()` SHALL treat that response as success
- **AND** the resource SHALL be recorded in Pulumi state with a fresh `activatedAt` timestamp

#### Scenario: Re-apply with unchanged inputs is a Pulumi-graph no-op

- **WHEN** Pulumi re-applies the stack and the `ZitadelSmtpActivation` resource's inputs (`smtpConfigId`, `domain`, `jwtProfileJson`) are unchanged from the previous apply
- **THEN** Pulumi's input diff SHALL be empty
- **AND** no lifecycle handler (`create` / `update` / `delete` / `read`) on `ZitadelSmtpActivation` SHALL be invoked
- **AND** zero HTTP traffic SHALL be generated against the Zitadel admin API
- **AND** the Pulumi state graph SHALL continue to record the resource as up-to-date

#### Scenario: Activation runs on a fresh Zitadel rebuild without operator intervention

- **WHEN** the dev (or future staging / prod) Zitadel instance is destroyed and recreated from scratch
- **AND** Pulumi runs `pulumi up` against the recreated instance
- **THEN** the `SmtpConfig` resource SHALL be recreated
- **AND** the `ZitadelSmtpActivation` resource SHALL fire `_activate` automatically as the next step in the dependency graph
- **AND** the operator SHALL NOT need to run any manual `curl` or `gcloud` step
- **AND** the first user sign-up after the rebuild SHALL receive a verification email

## REMOVED Requirements

### Requirement: Auto-Verify Email on Self-Registration

**Reason**: The auto-verify-email Action was removed during cutover (cloud-provisioning#215) because of two compounding issues:

1. **Mechanism is broken in Zitadel v4**: `request:*` Executions REPLACE the request body with the webhook response (not merge-patch). Returning `{ email: { is_verified: true } }` from the backend webhook therefore strips Profile, Phone, password, etc. from the `AddHumanUser` request, and the API validator rejects the result with `invalid AddHumanUserRequest.Profile: value is required`. See https://github.com/zitadel/zitadel/issues/9748 for the analogous bug report on `RetrieveIdentityProviderIntent`.

2. **Never delivered the intended UX**: Empirically, even on the old Zitadel Cloud setup the Action did not actually mark emails as verified — users were still prompted for the email-verification OTP during sign-up. The optimization the Action was supposed to provide was never observed working.

**Migration**: Email verification proceeds via Zitadel's default OTP step. Sign-up users receive a verification email after registration; entering the OTP marks the email as verified. Acceptable for dev. If passkey-only sign-ups should skip the email-verification screen later, the proper fix is either:
- Disable the email-verification step at the LoginPolicy level, OR
- Reconstruct the FULL `AddHumanUserRequest` in the webhook response (parse the JWT body, mutate `email.is_verified`, return the entire request payload — not just the email field).

The removal also collapses the `Provision Actions v2 Target and Execution Resources` requirement: only the `pre-access-token-webhook` Target + `ExecutionFunction` remain. The `auto-verify-email-webhook` Target + `ExecutionRequest` are deleted.
