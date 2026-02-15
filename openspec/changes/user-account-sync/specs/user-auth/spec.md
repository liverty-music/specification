## MODIFIED Requirements

### Requirement: Sign Up / Sign In

The system SHALL provide a mechanism for users to authenticate via the Zitadel Hosted UI using OIDC.

#### Scenario: Initiate Login

- **WHEN** user clicks the "Sign In" or "Sign Up" button
- **THEN** the system redirects the user to the configured Zitadel Issuer URL
- **AND** the request includes the correct Client ID and PKCE challenge

#### Scenario: Initiate Registration

- **WHEN** user clicks the "Sign Up" button
- **THEN** the system SHALL pass `state: { isRegistration: true }` in the OIDC redirect request
- **AND** the system SHALL use `prompt: 'create'` to show the Zitadel registration form

#### Scenario: Handle Login Callback

- **WHEN** the user is redirected back to `/auth/callback` after successful authentication
- **THEN** the system exchanges the authorization code for ID/Access tokens
- **AND** updates the application state to "Authenticated"
- **AND** redirects the user to the home page (or strict post-login route)

#### Scenario: Handle Registration Callback

- **WHEN** the user is redirected back to `/auth/callback` after successful registration
- **AND** `state.isRegistration` is `true`
- **THEN** the system exchanges the authorization code for ID/Access tokens
- **AND** calls the backend `Create` RPC with the user's `external_id` (from `sub` claim), `email`, and `name` from the token claims
- **AND** updates the application state to "Authenticated"
- **AND** redirects the user to the home page

#### Scenario: Registration Callback API Failure

- **WHEN** the `Create` RPC call fails during the registration callback (except `ALREADY_EXISTS`)
- **THEN** the system SHALL log the error
- **AND** the system SHALL still complete the authentication flow (user can use the app)
- **AND** the local user record will be created on a subsequent provisioning attempt

#### Scenario: Registration Callback Duplicate User

- **WHEN** the `Create` RPC returns `ALREADY_EXISTS` during the registration callback
- **THEN** the system SHALL treat this as a successful provisioning (no error logged)
- **AND** continue the normal authentication flow
