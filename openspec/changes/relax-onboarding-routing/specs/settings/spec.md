## MODIFIED Requirements

### Requirement: Sign Out
The system SHALL allow authenticated users to sign out of their account. The Sign Out control SHALL be rendered only when the user is authenticated and SHALL be hidden for guest (unauthenticated) users.

#### Scenario: Sign out action
- **WHEN** an authenticated user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list

#### Scenario: Sign out hidden for guests
- **WHEN** an unauthenticated (guest) user views the Settings page
- **THEN** the system SHALL NOT render the Sign Out control

## ADDED Requirements

### Requirement: Guest-Adaptive Account Section

The system SHALL render the Settings ACCOUNT section conditionally on authentication state. For guests, the section SHALL present a sign-in / sign-up call to action and SHALL hide account-bound controls (email address, email verification status, resend-verification, sign-out). For authenticated users, the section SHALL present the existing account controls.

#### Scenario: Guest sees auth entry in ACCOUNT section

- **WHEN** an unauthenticated user views the Settings page
- **THEN** the ACCOUNT section SHALL present a "ログイン / 新規登録" call to action that initiates the OIDC sign-in / sign-up flow
- **AND** the email address row, email-verification badge, and resend-verification button SHALL NOT be rendered

#### Scenario: Authenticated user sees account controls

- **WHEN** an authenticated user views the Settings page
- **THEN** the ACCOUNT section SHALL render the email address, the verification badge, the resend-verification button (when unverified), and the Sign Out control

### Requirement: Guest Language Preference

The system SHALL allow a guest user to change the display language from Settings. For guests, the change SHALL apply via `I18N.setLocale()` only and SHALL NOT call `UserService.UpdatePreferredLanguage` (no backend persistence is possible without an account).

#### Scenario: Guest changes language

- **WHEN** an unauthenticated user selects a language different from the current one
- **THEN** the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** all UI text SHALL immediately update to the selected language
- **AND** the system SHALL NOT call `UserService.UpdatePreferredLanguage`

#### Scenario: Guest home area sourced from guest storage

- **WHEN** an unauthenticated user views or changes "My Home Area"
- **THEN** the system SHALL read and write the home-area code via guest storage rather than the backend User entity
