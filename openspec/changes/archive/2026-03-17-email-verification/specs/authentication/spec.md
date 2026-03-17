## ADDED Requirements

### Requirement: Email Verified Claim Injection

The system SHALL inject the `email_verified` claim into JWT access tokens via a Zitadel Action at the `PRE_ACCESS_TOKEN_CREATION` trigger, alongside the existing `email` claim.

**Rationale**: Zitadel does not include `email_verified` in access tokens by default. The backend requires this claim to enforce email verification at the API layer.

#### Scenario: Human user with verified email

- **WHEN** a human user with a verified email address requests an access token
- **THEN** the Zitadel Action SHALL set `email_verified` claim to `true` in the access token

#### Scenario: Human user with unverified email

- **WHEN** a human user with an unverified email address requests an access token
- **THEN** the Zitadel Action SHALL set `email_verified` claim to `false` in the access token

#### Scenario: Machine user (service account)

- **WHEN** a machine user requests an access token
- **THEN** the Zitadel Action SHALL skip `email_verified` injection (no `human` field present)
- **AND** the token SHALL be issued without the `email_verified` claim

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

## MODIFIED Requirements

### Requirement: JWT Token Validation

The system SHALL validate JWT tokens from ZITADEL using the JWKS endpoint.

**Rationale**: Industry-standard JWT validation ensures secure authentication without requiring direct integration with the identity provider for every request.

#### Scenario: Valid Token

- **WHEN** a request includes a valid JWT token in the Authorization header
- **THEN** the system validates the token signature using ZITADEL's public keys
- **AND** verifies the issuer matches the configured ZITADEL instance
- **AND** verifies the token has not expired
- **AND** extracts the user ID from the `sub` claim
- **AND** extracts the `email_verified` claim from the token's private claims

#### Scenario: Invalid Token

- **WHEN** a request includes an invalid or expired JWT token
- **THEN** the system rejects the request with `connect.CodeUnauthenticated`
- **AND** logs the authentication failure for security monitoring
