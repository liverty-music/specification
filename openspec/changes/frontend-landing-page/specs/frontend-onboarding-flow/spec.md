## MODIFIED Requirements

### Requirement: Landing Page with Authentication
The system SHALL provide a landing page that communicates the service value proposition and enables user authentication via Zitadel (Passkey authentication), with post-authentication routing based on onboarding completion status.

#### Scenario: First-time user visits landing page
- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("大好きなあのバンドのライブ、もう二度と見逃さない。")
- **AND** the system SHALL display a sub-message ("あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。")
- **AND** the system SHALL provide "Sign Up" and "Sign In" buttons for Passkey authentication
- **AND** the system SHALL NOT provide Google, Spotify, Apple Music, or YouTube OAuth (out of MVP scope)

#### Scenario: User initiates Passkey authentication via Zitadel
- **WHEN** a user clicks the "Sign Up" or "Sign In" button
- **THEN** the system SHALL redirect the user to Zitadel OIDC flow for Passkey authentication
- **AND** upon successful authentication, Zitadel SHALL create or retrieve the user account
- **AND** the system SHALL check onboarding completion status
- **AND** if incomplete, the system SHALL redirect to the Artist Discovery step
- **AND** if complete, the system SHALL redirect to the Dashboard
