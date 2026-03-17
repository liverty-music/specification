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

#### Scenario: Invalid Token

- **WHEN** a request includes an invalid or expired JWT token
- **THEN** the system rejects the request with `connect.CodeUnauthenticated`
- **AND** logs the authentication failure for security monitoring

## ADDED Requirements

### Requirement: email_verified claim injection in access token

The Zitadel Action `addEmailClaim` SHALL inject the `email_verified` claim into JWT access tokens alongside the existing `email` claim. The value MUST reflect the user's `isEmailVerified` status from the Zitadel user object.

#### Scenario: Verified user receives email_verified=true

- **WHEN** a user with a verified email address authenticates
- **THEN** the issued access token SHALL contain `"email_verified": true`
- **AND** the existing `email` claim SHALL continue to be present

#### Scenario: Unverified user receives email_verified=false

- **WHEN** a user with an unverified email address authenticates
- **THEN** the issued access token SHALL contain `"email_verified": false`
- **AND** the existing `email` claim SHALL continue to be present

#### Scenario: Machine user token is unaffected

- **WHEN** a machine user (service account) authenticates
- **THEN** the access token SHALL NOT contain `email_verified` claim
- **AND** the existing guard for missing `human` field SHALL prevent errors
