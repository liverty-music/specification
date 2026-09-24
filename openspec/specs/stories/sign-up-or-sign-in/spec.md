# Sign up or sign in

## Purpose

Defines user authentication behavior: sign up / sign in, session restoration on cold start, and the server-side session monitoring policy.

## Requirements

### Requirement: Sign Up / Sign In

The system SHALL provide Passkey authentication via Zitadel. For new users, authentication is triggered at the end of the onboarding tutorial (Step 6) via a non-dismissible modal. For returning users, authentication is available via a [Login] link on the landing page.

#### Scenario: Initiate Login from Landing Page

- **WHEN** user clicks the [Login] link on the landing page
- **THEN** the system SHALL redirect the user to the configured Zitadel Issuer URL
- **AND** the request SHALL include the correct Client ID and PKCE challenge

#### Scenario: Initiate Registration from Tutorial Step 6

- **WHEN** the onboarding tutorial reaches Step 6
- **THEN** the system SHALL display a non-dismissible Passkey authentication modal
- **AND** the system SHALL use `prompt: 'create'` to show the Zitadel registration form
- **AND** the modal SHALL display the message: "All set! Create an account to save your preferences and never miss a live show."

#### Scenario: Handle Login Callback

- **WHEN** the user is redirected back to `/auth/callback` after successful authentication
- **THEN** the system SHALL exchange the authorization code for ID/Access tokens
- **AND** the system SHALL load the user profile via `ensureLoaded()`
- **AND** the system SHALL update the application state to "Authenticated"
- **AND** the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: Handle Registration Callback from Tutorial

- **WHEN** the user is redirected back to `/auth/callback` after successful registration from the tutorial
- **THEN** the system SHALL exchange the authorization code for ID/Access tokens
- **AND** the system SHALL attempt to load the user profile via `ensureLoaded()`
- **AND** when `ensureLoaded()` returns NotFound, the system SHALL call `provisionUser()` to create the backend user record
- **AND** the system SHALL trigger the guest data merge process
- **AND** upon merge completion, set `onboardingStep` to COMPLETED
- **AND** the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: Registration Callback API Failure

- **WHEN** the `Create` RPC call fails during the registration callback, including `ALREADY_EXISTS` because the email belongs to another identity
- **THEN** the system SHALL log the error
- **AND** the system SHALL still complete the authentication flow (user can use the app)
- **AND** the local user record will be created on a subsequent provisioning attempt

#### Scenario: Registration Callback for an already registered identity

- **WHEN** the signed-in identity already has an account and `Create` is called during the callback
- **THEN** `Create` returns the existing account unchanged
- **AND** the system SHALL continue exactly as for a newly created account

### Requirement: Every sign-in resolves the account with Create

After a sign-in, whether at the end of the tutorial or through the Login link, when the app remembers no account for the signed-in identity, it SHALL call UserUseCase.Create with the app's current display language as preferred language and, when the guest chose a home during onboarding, that home, and SHALL remember the returned account for that identity. Create is the one call that both registers a new identity and returns an existing one, so a returning fan is treated the same as a new one. Signing out SHALL forget the remembered account, so the next sign-in resolves it with Create again. After the account is resolved, the guest's follows and hype levels are merged as the story stories/merge-guest-data-on-signup describes.

#### Scenario: New fan finishes the tutorial

- **WHEN** a guest who chose home JP-13 during onboarding and uses the app in Japanese signs up at the end of the tutorial
- **THEN** a new account is created with home JP-13 and preferred language `ja`, and the app uses it from then on

#### Scenario: Returning fan signs in on a new device

- **WHEN** a fan with an account whose language is `en` signs in through the Login link on a device set to Japanese
- **THEN** the app uses the existing account and its preferred language stays `en`

#### Scenario: Sign out and back in

- **WHEN** a fan signs out and signs in again with the same identity
- **THEN** the app resolves the same account again and shows the fan's own follows
