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

### Requirement: Logout

The system SHALL provide a logout flow that ends the Zitadel session and redirects the user back to the application.

#### Scenario: Successful logout

- **WHEN** an authenticated user triggers logout
- **THEN** the system SHALL call the Zitadel `end_session` endpoint with a valid `id_token_hint`
- **AND** the `post_logout_redirect_uri` SHALL include a trailing `/` to match the Zitadel-registered URI exactly (e.g., `https://dev.liverty-music.app/`)
- **AND** upon successful session end, the user SHALL be redirected to the application root

#### Scenario: Logout redirect URI mismatch

- **WHEN** the `post_logout_redirect_uri` does not exactly match the URI registered in Zitadel
- **THEN** Zitadel SHALL return a 400 Bad Request with `invalid_request`
- **AND** the user will remain on the Zitadel error page

### Requirement: UserService.Get resolves caller from JWT

The `UserService.Get` RPC SHALL resolve the authenticated caller from JWT claims instead of requiring an explicit `user_id` parameter. This aligns with the pattern used by `UpdateHome`.

#### Scenario: Get own profile

- **WHEN** an authenticated user calls `UserService.Get` with no parameters
- **THEN** the backend SHALL extract the `sub` claim from the JWT context
- **AND** SHALL look up the user by external ID
- **AND** SHALL return the full `User` entity including `home` if set

#### Scenario: Unauthenticated Get request

- **WHEN** `UserService.Get` is called without valid authentication
- **THEN** the system SHALL return `UNAUTHENTICATED`

#### Scenario: User not found

- **WHEN** `UserService.Get` is called with a valid JWT but no matching user record exists
- **THEN** the system SHALL return `NOT_FOUND`
