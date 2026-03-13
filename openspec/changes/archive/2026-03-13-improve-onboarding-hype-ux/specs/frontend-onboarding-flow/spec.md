## MODIFIED Requirements

### Requirement: Landing Page with Authentication

The system SHALL provide a landing page that communicates the service value proposition and provides entry points for both new users (tutorial) and returning users (direct login). Authentication is no longer required at the landing page; new users enter a guest tutorial flow. The tutorial completes at Step 5 (My Artists) with signup prompted via notification dialog and inline banners.

#### Scenario: First-time user visits landing page

- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("大好きなあのバンドのライブ、もう二度と見逃さない。")
- **AND** the system SHALL display a sub-message ("あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。")
- **AND** the system SHALL provide a primary [Get Started] CTA button that enters the tutorial flow without authentication
- **AND** the system SHALL provide a secondary [Login] text link for returning users
- **AND** the system SHALL NOT provide "Sign Up" or "Sign In" buttons that trigger immediate authentication

#### Scenario: User taps Get Started

- **WHEN** a user taps the [Get Started] button
- **THEN** the system SHALL set `onboardingStep` to 1 in LocalStorage
- **AND** the system SHALL navigate to the Artist Discovery page (`/onboarding/discover`)
- **AND** the system SHALL NOT require authentication

#### Scenario: User taps Login

- **WHEN** a user taps the [Login] link
- **THEN** the system SHALL initiate the Zitadel OIDC flow for Passkey authentication
- **AND** upon successful authentication, the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: User provisioning fails during login callback

- **WHEN** the OIDC callback processing fails
- **THEN** the system SHALL display an error message on the callback page
- **AND** the system SHALL provide a "Return to Home" link

## REMOVED Requirements

### Requirement: Step 6 - SignUp modal display (from frontend-onboarding-flow perspective)

**Reason**: The forced signup modal at Step 6 is removed. Onboarding completes at Step 5 (coachmark dismissal). Signup is prompted via optional notification dialog and persistent inline banners on My Artists and Dashboard pages.
**Migration**: Remove Step 6 modal rendering from the onboarding flow. If `onboardingStep=6` is found in localStorage, advance to 7 (COMPLETED). Signup CTA is now in the notification dialog and `signup-prompt-banner` component.
