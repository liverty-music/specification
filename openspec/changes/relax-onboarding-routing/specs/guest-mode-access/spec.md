## ADDED Requirements

### Requirement: Guest Free Navigation After Dashboard

The system SHALL allow an unauthenticated (guest) user who has reached the dashboard to navigate to any application route, including routes that surface account-bound features (e.g. Settings, Tickets). Navigation SHALL NOT be hard-blocked on the basis of guest status alone.

#### Scenario: Guest navigates to Tickets after dashboard

- **WHEN** a guest user has `onboardingStep` of `'dashboard'`, `'my-artists'`, or `'completed'`
- **AND** the user taps the Tickets nav tab
- **THEN** the system SHALL allow the Tickets route to load
- **AND** the system SHALL render the Tickets screen's existing empty / unauthenticated state rather than redirecting away

#### Scenario: Guest navigates to Settings after dashboard

- **WHEN** a guest user has reached at least the `'dashboard'` step
- **AND** the user taps the Settings nav tab
- **THEN** the system SHALL allow the Settings route to load

### Requirement: Account-Only Features Hidden, Not Blocked

The system SHALL hide features that require an authenticated account from the guest UI rather than blocking navigation to the screen or surfacing an error/login-required toast at the point of a blocked action. Each screen SHALL define which of its affordances are account-only and omit them from the rendered guest UI.

#### Scenario: Account-only affordance is absent for guests

- **WHEN** a guest user views a screen that contains an account-only feature (e.g. email verification, sign-out, ticket management)
- **THEN** the system SHALL NOT render that affordance
- **AND** the system SHALL NOT render a disabled control that emits a "login required" error when tapped

#### Scenario: Account-only affordance appears once authenticated

- **WHEN** the same screen is viewed by an authenticated user
- **THEN** the system SHALL render the account-only affordance

### Requirement: Persistent Auth Entry From Discovery Onward

The system SHALL provide an always-reachable sign-in / sign-up entry point for guests from the `'discovery'` step onward, so a returning user who entered the guest flow can authenticate without completing onboarding. This entry point is hosted in Settings (see `settings` spec).

#### Scenario: Guest reaches auth entry during early onboarding

- **WHEN** a guest user is at the `'discovery'` step or later
- **AND** the user opens Settings
- **THEN** the system SHALL present a sign-in / sign-up call to action

#### Scenario: Returning user recovers from mis-tapping Get Started

- **WHEN** a user taps [Get Started] on Welcome and enters the guest discovery step
- **AND** the user actually intended to log in
- **THEN** the user SHALL be able to open Settings and start sign-in without first satisfying any onboarding progression condition
