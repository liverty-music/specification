## MODIFIED Requirements

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
- **AND** the system SHALL update the application state to "Authenticated"
- **AND** the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: Handle Registration Callback from Tutorial

- **WHEN** the user is redirected back to `/auth/callback` after successful registration from the tutorial
- **THEN** the system SHALL exchange the authorization code for ID/Access tokens
- **AND** the system SHALL trigger the guest data merge process
- **AND** upon merge completion, set `onboardingStep` to COMPLETED
- **AND** the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: Registration Callback API Failure

- **WHEN** the `Create` RPC call fails during the registration callback (except `ALREADY_EXISTS`)
- **THEN** the system SHALL log the error
- **AND** the system SHALL still complete the authentication flow (user can use the app)
- **AND** the local user record will be created on a subsequent provisioning attempt

#### Scenario: Registration Callback Duplicate User

- **WHEN** the `Create` RPC returns `ALREADY_EXISTS` during the registration callback
- **THEN** the system SHALL treat this as a successful provisioning (no error logged)
- **AND** the system SHALL continue the normal authentication flow

## REMOVED Requirements

### Requirement: Sign Up and Sign In buttons on Landing Page

**Reason**: Replaced by the linear tutorial flow. New users enter via [Get Started] (no auth) and authenticate at Step 6. Returning users use [Login] link.
**Migration**: The [Login] link on the LP replaces the previous "Sign In" button. The "Sign Up" button is removed entirely; registration occurs via the tutorial Step 6 modal.
