## MODIFIED Requirements

### Requirement: Passkey Authentication CTA

The system SHALL provide a primary [Get Started] CTA for new users entering the tutorial and a secondary [Login] link for returning users. The CTA displayed SHALL vary based on `onboardingStep` and `isAuthenticated` state.

#### Scenario: New user or tutorial-in-progress user sees LP

- **WHEN** an unauthenticated user visits `/`
- **AND** `onboardingStep` is unset, 0, or between 1 and 5
- **THEN** the system SHALL display a primary [Get Started] CTA button
- **AND** the system SHALL display a secondary [Login] text link below the primary CTA
- **AND** the primary CTA SHALL use the brand accent color with a glow/shadow effect
- **AND** the secondary link SHALL use a subtle text style

#### Scenario: Completed user with expired token sees LP

- **WHEN** an unauthenticated user visits `/`
- **AND** `onboardingStep` is COMPLETED (7)
- **THEN** the system SHALL display a primary [Login] CTA button
- **AND** the system SHALL NOT display the [Get Started] button

#### Scenario: User at Step 6 accesses LP

- **WHEN** an unauthenticated user visits `/`
- **AND** `onboardingStep` is 6
- **THEN** the system SHALL immediately display the non-dismissible SignUp modal
- **AND** the system SHALL NOT display the LP hero content behind the modal

#### Scenario: No alternative auth methods displayed

- **WHEN** the landing page is displayed
- **THEN** the system SHALL NOT display email/password fields or social login buttons (Google, Spotify, etc.)
- **AND** Passkey SHALL be the sole authentication method

### Requirement: Authenticated User Redirect

The system SHALL redirect already-authenticated users away from the landing page to the Dashboard, regardless of `onboardingStep` value.

#### Scenario: Authenticated user visits landing page

- **WHEN** an authenticated user navigates to `/`
- **THEN** the system SHALL redirect to the Dashboard with full unrestricted access
- **AND** the system SHALL NOT check `onboardingStep`

#### Scenario: Redirect target check fails

- **WHEN** the redirect fails due to a network or API error
- **THEN** the system SHALL display the landing page with an error toast: "Could not determine account status. Please try signing in again."
- **AND** the system SHALL NOT crash to a white screen
- **AND** the system SHALL allow the user to manually navigate via the Login link
