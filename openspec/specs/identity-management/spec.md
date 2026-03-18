# Identity Management

## Purpose

Manage identity, authentication, and authorization policies for the Liverty Music platform.

## Requirements

### Requirement: Manage Zitadel Organization

The system SHALL manage the Zitadel organization configuration via Infrastructure as Code to ensure consistency and reproducibility.

#### Scenario: Provision Organization

- **WHEN** Pulumi stack is applied
- **THEN** the Zitadel organization defined in the configuration SHALL exist

### Requirement: Manage Zitadel Project

The system SHALL manage the `liverty-music` project within the Zitadel organization to group related resources.

#### Scenario: Provision Project

- **WHEN** Pulumi stack is applied
- **THEN** a project named `liverty-music` SHALL exist in the organization

### Requirement: Manage OIDC Application

The system SHALL manage the OIDC application for the frontend SPA within the `liverty-music` project to enable user authentication.

#### Scenario: Provision OIDC App

- **WHEN** Pulumi stack is applied
- **THEN** an OIDC application named `liverty-music` SHALL exist
- **AND** the application Type SHALL be "SPA"
- **AND** the Auth Method Type SHALL be "NONE"

### Requirement: Configure Login Policy

The system SHALL establish a login policy that enforces passwordless authentication to improve user security and eliminate reliance on passwords.

#### Scenario: Apply Strict Passkeys Policy

- **WHEN** Pulumi stack is applied
- **THEN** the default login policy for the organization SHALL be configured
- **AND** `PasswordlessType` SHALL be "ALLOWED"
- **AND** `UserLogin` SHALL be false (Enforces Passkeys-only)
- **AND** `AllowExternalIdp` SHALL be false

### Requirement: Auto-Verify Email on Self-Registration

The system SHALL automatically mark a user's email as verified before account creation during Zitadel Self-Registration, via a Zitadel Action on the `INTERNAL_AUTHENTICATION / PRE_CREATION` flow that calls `api.setEmailVerified(true)`.

**Rationale**: Zitadel's Hosted Login blocks the OIDC authorization flow with an OTP step when SMTP is configured and email is unverified. Setting email as verified before creation skips this step, allowing the OIDC flow to complete immediately after passkey registration. The `LoginPolicy` resource does not expose an email verification toggle.

#### Scenario: New user registers via Self-Registration

- **WHEN** a new user completes Self-Registration (email + passkey)
- **THEN** the `PRE_CREATION` Zitadel Action SHALL call `api.setEmailVerified(true)` before user creation
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
