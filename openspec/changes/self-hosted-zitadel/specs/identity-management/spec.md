## ADDED Requirements

### Requirement: Inject Email Claim into Access Tokens via Actions v2

The system SHALL inject the authenticated user's `email` claim into every issued JWT access token by configuring a Zitadel Actions v2 `ExecutionFunction` bound to the `preaccesstoken` function, pointing at the backend `/pre-access-token` webhook Target.

**Rationale**: Zitadel does not include `email` in access tokens by default; the backend JWT validator requires this claim for user provisioning. Injection previously occurred via an Actions v1 JavaScript function (`addEmailClaim`); migrating to Actions v2 aligns with the upstream deprecation of v1 and moves the logic into a testable backend handler.

#### Scenario: Access token issued to a human user contains email

- **WHEN** a human user completes the OIDC authorization flow
- **THEN** the issued JWT access token SHALL contain an `email` claim equal to the user's verified email address

#### Scenario: Access token issued to a machine user omits email

- **WHEN** a machine user obtains an access token via client-credentials
- **THEN** the issued JWT access token SHALL NOT contain an `email` claim
- **AND** the token issuance SHALL succeed

### Requirement: Provision Actions v2 Target and Execution Resources

The system SHALL manage the Zitadel Actions v2 `Target` and `ExecutionFunction` resources for email-claim injection via Infrastructure as Code, using a Pulumi Dynamic Resource that calls the Zitadel REST API because the installed `@pulumiverse/zitadel` provider does not yet expose Actions v2 resource types.

**Rationale**: Managing these resources declaratively alongside existing v1 resources (Project, ApplicationOidc, LoginPolicy) preserves drift detection and reproducibility across rebuilds.

#### Scenario: Pulumi apply creates Actions v2 resources

- **WHEN** the Pulumi stack is applied
- **THEN** a Zitadel Actions v2 Target named `pre-access-token-webhook` SHALL exist pointing at the backend `/pre-access-token` endpoint
- **AND** a Zitadel Actions v2 ExecutionFunction SHALL bind the `preaccesstoken` function to that Target

#### Scenario: Targets use JWT payload authentication

- **WHEN** a Target is created by Pulumi
- **THEN** the Target's `payloadType` SHALL be `PAYLOAD_TYPE_JWT`
- **AND** the Target SHALL NOT be configured with a shared `signingKey`

### Requirement: Dedicated Service User for Login V2 UI

The system SHALL provision a Zitadel `MachineUser` named `login-client` with `IAM_LOGIN_CLIENT` instance-level role and a long-lived `PersonalAccessToken`, mounted into the `zitadel-login` Pod as a file referenced by the `ZITADEL_SERVICE_USER_TOKEN_FILE` environment variable.

**Rationale**: The self-hosted Zitadel Login V2 UI (Next.js, separate container from the Zitadel API) calls privileged settings + cross-org user-search APIs at SSR time and cannot use end-user OIDC tokens. Without a service-user PAT, the Login UI's SSR returns HTTP 500 with `fetch() returned undefined` from every settings call, breaking every login flow. This requirement was missing from the original cutover plan because Zitadel Cloud handles the Login UI's authentication internally; in self-hosted, the Login UI must be registered as a first-class API client. See https://zitadel.com/docs/self-hosting/manage/login-client.

#### Scenario: Login UI authenticates to Zitadel API on every SSR request

- **WHEN** the `zitadel-login` Pod handles a `/ui/v2/login/*` route
- **THEN** the Next.js server SHALL read the PAT from the file referenced by `ZITADEL_SERVICE_USER_TOKEN_FILE`
- **AND** SHALL include it as a Bearer token on outgoing API calls
- **AND** the Zitadel API SHALL accept the token and return the requested settings / user data

#### Scenario: PAT is mounted as a file, not an env var value

- **WHEN** the K8s manifest sets up the PAT
- **THEN** the K8s Secret data key SHALL be projected to a file at `/var/run/zitadel/login-client.pat`
- **AND** the env var `ZITADEL_SERVICE_USER_TOKEN_FILE` SHALL point at that path
- **AND** the env var `ZITADEL_SERVICE_USER_TOKEN` SHALL NOT be set, so that the PAT does not appear in `kubectl describe pod` env dumps

#### Scenario: PAT has no expiration in dev

- **WHEN** Pulumi creates the `login-client` `PersonalAccessToken` for `dev`
- **THEN** `expirationDate` SHALL be omitted (Zitadel treats this as never-expires)
- **AND** an inline comment in the Pulumi component SHALL document that staging / prod must adopt a real expiration + rotation runbook before extending the cutover beyond dev

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password reset emails, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the API call to send the email returns success (202-equivalent), the notification worker logs nothing, and the user-facing UX is "no email arrived." Discovered during the dev cutover smoke test when sign-up succeeded but verification emails never reached Postmark. The implementation contract is pinned to the Dynamic Resource (rather than "Dynamic Resource OR equivalent") so a manual `curl` step cannot be a "valid implementation" — every Zitadel rebuild must activate SMTP declaratively without operator memory.

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

## REMOVED Requirements

### Requirement: Auto-Verify Email on Self-Registration

**Reason**: The auto-verify-email Action was removed during cutover (cloud-provisioning#215) because of two compounding issues:

1. **Mechanism is broken in Zitadel v4**: `request:*` Executions REPLACE the request body with the webhook response (not merge-patch). Returning `{ email: { is_verified: true } }` from the backend webhook therefore strips Profile, Phone, password, etc. from the `AddHumanUser` request, and the API validator rejects the result with `invalid AddHumanUserRequest.Profile: value is required`. See https://github.com/zitadel/zitadel/issues/9748 for the analogous bug report on `RetrieveIdentityProviderIntent`.

2. **Never delivered the intended UX**: Empirically, even on the old Zitadel Cloud setup the Action did not actually mark emails as verified — users were still prompted for the email-verification OTP during sign-up. The optimization the Action was supposed to provide was never observed working.

**Migration**: Email verification proceeds via Zitadel's default OTP step. Sign-up users receive a verification email after registration; entering the OTP marks the email as verified. Acceptable for dev. If passkey-only sign-ups should skip the email-verification screen later, the proper fix is either:
- Disable the email-verification step at the LoginPolicy level, OR
- Reconstruct the FULL `AddHumanUserRequest` in the webhook response (parse the JWT body, mutate `email.is_verified`, return the entire request payload — not just the email field).

The removal also collapses the `Provision Actions v2 Target and Execution Resources` requirement: only the `pre-access-token-webhook` Target + `ExecutionFunction` remain. The `auto-verify-email-webhook` Target + `ExecutionRequest` are deleted.
