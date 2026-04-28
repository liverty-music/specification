## MODIFIED Requirements

### Requirement: Auto-Verify Email on Self-Registration

The system SHALL automatically mark a user's email as verified before account creation during Zitadel Self-Registration, via a Zitadel Actions v2 `Execution` + `Target` that invokes a backend webhook mutating the user-creation request to set the email as verified prior to user creation by the Zitadel core.

**Rationale**: Zitadel's Hosted Login blocks the OIDC authorization flow with an OTP step when SMTP is configured and email is unverified. Setting email as verified before creation skips this step, allowing the OIDC flow to complete immediately after passkey registration. The Actions v1 JavaScript mechanism previously used for this purpose is deprecated in Zitadel v4 and migrates to the Actions v2 Execution/Target model.

#### Scenario: New user registers via Self-Registration

- **WHEN** a new user completes Self-Registration (email + passkey)
- **THEN** the Actions v2 request-execution target SHALL receive the user-creation payload before Zitadel persists the user
- **AND** the target webhook SHALL set the email as verified in the forwarded request
- **AND** the user SHALL be created with email already verified
- **AND** the OIDC authorization flow SHALL complete without an OTP step
- **AND** the user SHALL be redirected to `/auth/callback` immediately

#### Scenario: Webhook failure in production

- **GIVEN** the auto-verify Execution is configured with `interruptOnError: true` (the staging / prod default)
- **WHEN** the auto-verify webhook fails
- **THEN** the registration flow SHALL fail
- **AND** the error SHALL be logged for investigation

#### Scenario: Webhook failure in development

- **GIVEN** the auto-verify Execution is configured with `interruptOnError: false` (dev only)
- **WHEN** the auto-verify webhook fails
- **THEN** the registration flow SHALL continue
- **AND** the user MAY see the Zitadel OTP step as a fallback

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

The system SHALL manage the Zitadel Actions v2 `Target` and `ExecutionFunction` / `ExecutionRequest` resources (for both email-claim injection and auto-verify-email) via Infrastructure as Code, using a Pulumi Dynamic Resource that calls the Zitadel REST API because the installed `@pulumiverse/zitadel` provider does not yet expose Actions v2 resource types.

**Rationale**: Managing these resources declaratively alongside existing v1 resources (Project, ApplicationOidc, LoginPolicy) preserves drift detection and reproducibility across rebuilds.

#### Scenario: Pulumi apply creates Actions v2 resources

- **WHEN** the Pulumi stack is applied
- **THEN** a Zitadel Actions v2 Target named `pre-access-token-webhook` SHALL exist pointing at the backend `/pre-access-token` endpoint
- **AND** a Zitadel Actions v2 ExecutionFunction SHALL bind the `preaccesstoken` function to that Target
- **AND** a second Target and ExecutionRequest SHALL exist for the auto-verify-email flow

#### Scenario: Targets use JWT payload authentication

- **WHEN** a Target is created by Pulumi
- **THEN** the Target's `payloadType` SHALL be `PAYLOAD_TYPE_JWT`
- **AND** the Target SHALL NOT be configured with a shared `signingKey`

#### Scenario: Auto-verify-email backend endpoint validates the webhook JWT

- **WHEN** the backend `/auto-verify-email` endpoint receives a request from Zitadel
- **THEN** the endpoint SHALL apply the webhook-JWT validation contract defined in `authentication/spec.md` "Validate Zitadel Actions v2 Webhook JWTs"
- **AND** the validator SHALL pin the `aud` claim to `urn:liverty-music:webhook:auto-verify-email` (distinct from the end-user access-token audience and from the `pre-access-token` audience)
- **AND** a request whose JWT is a valid end-user access token, or a valid `pre-access-token` webhook JWT, SHALL be rejected with HTTP 401 because the `aud` does not match
- **AND** only a request whose JWT carries the `auto-verify-email` audience SHALL proceed to mutate the user-creation request

## REMOVED Requirements

**Note**: No requirement is removed by this change. The existing "Auto-Verify Email on Self-Registration" requirement is retained via the `MODIFIED Requirements` section above, with the implementation mechanism shifted from Actions v1 JavaScript to Actions v2 webhook. Removal of the underlying v1 Pulumi resources (`zitadel.Action`, `zitadel.TriggerActions`) is an implementation detail of the modified requirement, not a separate removed capability.
