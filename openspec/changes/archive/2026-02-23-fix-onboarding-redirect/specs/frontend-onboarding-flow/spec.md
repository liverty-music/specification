## MODIFIED Requirements

### Requirement: Landing Page with Authentication
The system SHALL provide a landing page that communicates the service value proposition and enables user authentication via Zitadel (Passkey authentication), with post-authentication routing based on sign-up detection.

#### Scenario: First-time user visits landing page
- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("大好きなあのバンドのライブ、もう二度と見逃さない。")
- **AND** the system SHALL display a sub-message ("あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。")
- **AND** the system SHALL provide "Sign Up" and "Sign In" buttons for Passkey authentication
- **AND** the system SHALL NOT provide Google, Spotify, Apple Music, or YouTube OAuth (out of MVP scope)

#### Scenario: User initiates Passkey authentication via Zitadel
- **WHEN** a user clicks the "Sign Up" or "Sign In" button
- **THEN** the system SHALL redirect the user to Zitadel OIDC flow for Passkey authentication
- **AND** upon successful authentication, the system SHALL check the OIDC state for the `isSignUp` flag
- **AND** if `isSignUp` is `true`, the system SHALL provision the user in the backend and redirect to the Artist Discovery step
- **AND** if `isSignUp` is `false` or absent, the system SHALL redirect to the Dashboard

#### Scenario: Authenticated user returns to landing page
- **WHEN** an authenticated user navigates to `/` or `/welcome`
- **THEN** the system SHALL redirect the user to `/dashboard`
- **AND** the system SHALL NOT check followed artist count for routing decisions

#### Scenario: User who unfollowed all artists signs in
- **WHEN** an existing user who has unfollowed all artists signs in
- **THEN** the system SHALL redirect the user to `/dashboard`
- **AND** the system SHALL NOT redirect the user to the Artist Discovery step
- **AND** the dashboard SHALL display its normal state (with region overlay if region is not configured)

## REMOVED Requirements

### Requirement: Onboarding Completion Check via Followed Artists
**Reason**: The implicit onboarding check based on followed artist count (`hasCompletedOnboarding()`) conflated "has followed artists" with "has completed onboarding". This caused users who unfollowed all artists to be incorrectly redirected back to the discovery page. Replaced by explicit sign-up detection via OIDC state.
**Migration**: Remove `hasCompletedOnboarding()` and `getRedirectTarget()` from `OnboardingService`. Use `isSignUp` OIDC state flag in `auth-callback.ts` for routing decisions. Remove dead `ONBOARDING_COMPLETE_KEY` localStorage key from `artist-discovery-page.ts`.
