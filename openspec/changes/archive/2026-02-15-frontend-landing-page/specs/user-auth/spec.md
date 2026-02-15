## MODIFIED Requirements

### Requirement: Sign Up / Sign In

The system SHALL provide a mechanism for users to authenticate via the Zitadel Hosted UI using OIDC.

#### Scenario: Initiate Login

- **WHEN** user clicks the "Sign Up" or "Sign In" button on the landing page
- **THEN** the system redirects the user to the configured Zitadel Issuer URL
- **AND** the request includes the correct Client ID and PKCE challenge

#### Scenario: Handle Login Callback with Onboarding Routing

- **WHEN** the user is redirected back to `/auth/callback` after successful authentication
- **THEN** the system exchanges the authorization code for ID/Access tokens
- **AND** updates the application state to "Authenticated"
- **AND** the system SHALL check if the user has ≥1 followed artist via `ListFollowedArtists` RPC
- **AND** if the user has no followed artists, the system SHALL redirect to the Artist Discovery page (`/onboarding/discover`)
- **AND** if the user has ≥1 followed artist, the system SHALL redirect to the Dashboard (`/dashboard`)
