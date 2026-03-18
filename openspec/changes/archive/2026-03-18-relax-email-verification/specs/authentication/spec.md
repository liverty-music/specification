## MODIFIED Requirements

### Requirement: Email Verified Claim Injection

The system SHALL inject the `email_verified` claim into JWT access tokens via a Zitadel Action at the `PRE_ACCESS_TOKEN_CREATION` trigger, alongside the existing `email` claim.

**Rationale**: Zitadel does not include `email_verified` in access tokens by default. The claim is preserved for future per-feature enforcement even though no current feature requires it.

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

## REMOVED Requirements

### Requirement: Backend Email Verification Enforcement

**Reason**: No current feature requires a verified email. Enforcing `email_verified` at the interceptor level blocks all RPC calls for unverified users, preventing service usage entirely. Future features that require verified email will enforce it at the use-case layer on a per-RPC basis.

**Migration**: Delete `EmailVerificationInterceptor` and remove it from the interceptor chain. The `Claims.EmailVerified` field and JWT extraction logic remain unchanged for future use.

### Requirement: Frontend Email Verification Check

**Reason**: The frontend gate signed out users with unverified email and displayed an error with no recovery path. With the backend enforcement also removed, this check serves no purpose and blocks legitimate users.

**Migration**: Remove the `email_verified` check and `signOut()` call from `auth-callback-route.ts`. Unverified users proceed through the normal provisioning and redirect flow.
