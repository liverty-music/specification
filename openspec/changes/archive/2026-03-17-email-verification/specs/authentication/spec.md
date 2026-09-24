## ADDED Requirements

### Requirement: Backend Email Verification Enforcement

The system SHALL reject authenticated requests where the access token's `email_verified` claim is not `true`, returning `connect.CodeUnauthenticated`.

**Rationale**: Defense-in-depth. Even though Zitadel's Hosted Login enforces email verification when SMTP is configured, the backend SHALL independently verify the claim to guard against API-created users or misconfigured identity providers.

#### Scenario: Request with verified email

- **WHEN** an authenticated request includes a valid JWT with `email_verified: true`
- **THEN** the system SHALL allow the request to proceed to the RPC handler
- **AND** the `EmailVerified` field SHALL be available in `Claims`

#### Scenario: Request with unverified email

- **WHEN** an authenticated request includes a valid JWT with `email_verified: false`
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the error message SHALL indicate that email verification is required

#### Scenario: Request with missing email_verified claim

- **WHEN** an authenticated request includes a valid JWT without the `email_verified` claim
- **THEN** the system SHALL reject the request with `connect.CodeUnauthenticated`
- **AND** the error message SHALL indicate that email verification is required

#### Scenario: Machine user token without email_verified

- **WHEN** an authenticated request uses a machine user token (no `email_verified` claim, no `email` claim)
- **THEN** the system SHALL allow the request if it passes existing validation
- **AND** the `email_verified` check SHALL be skipped for tokens without an `email` claim

### Requirement: Frontend Email Verification Check

The system SHALL verify the user's `email_verified` status during the OIDC callback and display an error if the email is not verified.

**Rationale**: Immediate user feedback. Rather than letting the user reach the dashboard and fail on every API call, the frontend SHALL catch unverified emails at the earliest opportunity and guide the user.

#### Scenario: Callback with verified email

- **WHEN** the OIDC callback processes a token where `email_verified` is `true` in the ID token profile
- **THEN** the system SHALL proceed with normal flow (provisioning, merge, redirect to dashboard)

#### Scenario: Callback with unverified email

- **WHEN** the OIDC callback processes a token where `email_verified` is `false` or missing in the ID token profile
- **THEN** the system SHALL NOT proceed to user provisioning or guest data merge
- **AND** the system SHALL display an error message instructing the user to verify their email
- **AND** the system SHALL provide a way to return to the login flow

