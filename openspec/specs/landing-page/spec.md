## Requirements

### Requirement: Passkey Authentication CTA

The system SHALL provide both a primary [Get Started] CTA and a secondary [Log In] CTA on every visit to the landing page for unauthenticated users. Both CTAs SHALL always be visible regardless of `onboardingStep` value. Both CTAs SHALL be rendered as `<button>` elements for accessibility.

#### Scenario: Any unauthenticated user sees both CTAs

- **WHEN** an unauthenticated user visits `/`
- **THEN** the system SHALL display a primary [Get Started] button
- **AND** the system SHALL display a secondary [Log In] button below the primary CTA
- **AND** the primary CTA SHALL use the brand accent color with a filled background
- **AND** the secondary CTA SHALL use an outline/ghost style with brand color text
- **AND** both buttons SHALL have a minimum tap target of 48px height

#### Scenario: Get Started initiates onboarding without clearing guest data

- **WHEN** an unauthenticated user taps [Get Started]
- **THEN** the system SHALL reset the onboarding step to DISCOVERY
- **AND** the system SHALL navigate to `/discovery`
- **AND** the system SHALL NOT clear previously stored guest artist data (`guest.follows`)

#### Scenario: Log In initiates OAuth sign-in

- **WHEN** an unauthenticated user taps [Log In]
- **THEN** the system SHALL initiate the Zitadel OIDC sign-in flow

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
- **AND** the system SHALL allow the user to manually navigate via the Log In button

### Requirement: Welcome Page Language Switcher

The landing page SHALL provide a language toggle for unauthenticated users to switch between supported locales without requiring sign-in.

#### Scenario: Language toggle visible on welcome page
- **WHEN** an unauthenticated user visits the welcome page
- **THEN** the system SHALL display a language toggle below the Log In button
- **AND** the toggle SHALL show all supported languages (EN, JA)
- **AND** the current active language SHALL be visually distinguished (e.g., bold or underline)

#### Scenario: Switching language on welcome page
- **WHEN** the user taps a language option
- **THEN** the system SHALL call `i18n.setLocale(lang)` to update all translated strings immediately
- **AND** the system SHALL persist the choice via `localStorage.setItem('language', lang)`
- **AND** no page reload SHALL be required

#### Scenario: Language preference persists across sessions
- **WHEN** the user selects a language on the welcome page and later returns
- **THEN** the i18next language detector SHALL read the persisted `language` key from localStorage
- **AND** the application SHALL start in the previously selected language
