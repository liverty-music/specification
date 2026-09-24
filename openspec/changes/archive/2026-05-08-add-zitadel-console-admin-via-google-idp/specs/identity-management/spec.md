## MODIFIED Requirements

### Requirement: Configure Login Policy

The system SHALL establish a login policy on the **`liverty-music` product
org** (the org that hosts the OIDC application and end-user accounts) that
enforces passwordless authentication to improve user security and
eliminate reliance on passwords. This policy SHALL apply ONLY to the
`liverty-music` product org and MUST NOT be inherited by the `admin` role
org, which has its own admin-oriented login policy governed by separate
requirements.

#### Scenario: Apply Strict Passkeys Policy on product org

- **WHEN** Pulumi stack is applied
- **THEN** the login policy for the `liverty-music` product org SHALL be
  configured
- **AND** `PasswordlessType` SHALL be "ALLOWED"
- **AND** `UserLogin` SHALL be false (Enforces Passkeys-only)
- **AND** `AllowExternalIdp` SHALL be false

#### Scenario: Admin org isolation

- **WHEN** the `liverty-music` product org login policy is applied
- **THEN** the policy SHALL NOT be applied to the `admin` role org
- **AND** the `admin` role org SHALL retain a separate login policy that
  allows external IdP sign-in (see "Configure Admin Org Login Policy")

### Requirement: Auto-Verify Email on Self-Registration

The system SHALL automatically mark a user's email as verified before
account creation during Zitadel Self-Registration in the `liverty-music`
product org, via a Zitadel Action on the
`INTERNAL_AUTHENTICATION / PRE_CREATION` flow that calls
`api.setEmailVerified(true)`.

**Rationale**: Zitadel's Hosted Login blocks the OIDC authorization flow
with an OTP step when SMTP is configured and email is unverified. Setting
email as verified before creation skips this step, allowing the OIDC flow
to complete immediately after passkey registration. The `LoginPolicy`
resource does not expose an email verification toggle.

#### Scenario: New end user registers via Self-Registration

- **WHEN** a new end user completes Self-Registration (email + passkey) in
  the `liverty-music` product org
- **THEN** the `PRE_CREATION` Zitadel Action SHALL call
  `api.setEmailVerified(true)` before user creation
- **AND** the user SHALL be created with email already verified
- **AND** the OIDC authorization flow SHALL complete without an OTP step
- **AND** the user SHALL be redirected to `/auth/callback` immediately

#### Scenario: Action failure in production

- **WHEN** the auto-verify Action fails in staging or production
- **THEN** the registration flow SHALL fail (`allowedToFail: false`)
- **AND** the error SHALL be logged for investigation

#### Scenario: Action failure in development

- **WHEN** the auto-verify Action fails in the dev environment
- **THEN** the registration flow SHALL continue (`allowedToFail: true`)
- **AND** the user MAY see the OTP step as a fallback
