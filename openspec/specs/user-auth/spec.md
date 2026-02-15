# User Authentication

## Purpose

The `user-auth` capability handles user identity management, including OIDC client configuration, session management, and UI integration for the Liverty Music platform.

## Requirements

### Requirement: Sign Up / Sign In

The system SHALL provide a mechanism for users to authenticate via the Zitadel Hosted UI using OIDC.

#### Scenario: Initiate Login

- **WHEN** user clicks the "Sign Up" or "Sign In" button on the landing page
- **THEN** the system redirects the user to the configured Zitadel Issuer URL
- **AND** the request includes the correct Client ID and PKCE challenge

#### Scenario: Initiate Registration

- **WHEN** user clicks the "Sign Up" button
- **THEN** the system SHALL pass `state: { isRegistration: true }` in the OIDC redirect request
- **AND** the system SHALL use `prompt: 'create'` to show the Zitadel registration form

#### Scenario: Handle Login Callback with Onboarding Routing

- **WHEN** the user is redirected back to `/auth/callback` after successful authentication
- **THEN** the system exchanges the authorization code for ID/Access tokens
- **AND** updates the application state to "Authenticated"
- **AND** the system SHALL check if the user has ≥1 followed artist via `ListFollowedArtists` RPC
- **AND** if the user has no followed artists, the system SHALL redirect to the Artist Discovery page (`/onboarding/discover`)
- **AND** if the user has ≥1 followed artist, the system SHALL redirect to the Dashboard (`/dashboard`)

#### Scenario: Handle Registration Callback

- **WHEN** the user is redirected back to `/auth/callback` after successful registration
- **AND** `state.isRegistration` is `true`
- **THEN** the system exchanges the authorization code for ID/Access tokens
- **AND** calls the backend `Create` RPC with the user's `email` parameter (backend extracts `external_id` and `name` from JWT)
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

### Requirement: Session Management

The system SHALL maintain the user's authentication state across page reloads and handle token expiration.

#### Scenario: Restore Session

- **WHEN** the application is loaded
- **THEN** the system checks for valid existing tokens
- **AND** if valid, restores the authenticated user session without requiring re-login

#### Scenario: Auto Sign-in (Silent Refresh)

- **WHEN** the access token is about to expire
- **THEN** the system attempts to renew the token silently using the Refresh Token

### Requirement: Sign Out

The system SHALL allow the user to terminate their session.

#### Scenario: Logout

- **WHEN** the user clicks "Sign Out"
- **THEN** the system clears local tokens
- **AND** redirects the user to the identity provider's end-session endpoint to clear the SSO session
