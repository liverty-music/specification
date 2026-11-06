# Spec Delta

## MODIFIED Requirements

### Requirement: Guest Free Navigation After Dashboard

The system SHALL allow an unauthenticated (guest) user who has reached the dashboard to navigate to any application route, including routes that surface account-bound features (e.g. Settings, Tickets). Navigation SHALL NOT be hard-blocked on the basis of guest status alone.

#### Scenario: Guest navigates to Tickets after dashboard

- **WHEN** a guest user has `onboardingStep` of `'dashboard'`, `'my-artists'`, or `'completed'`
- **AND** the user taps the Tickets nav tab
- **THEN** the system SHALL allow the Tickets route to load
- **AND** the system SHALL render the Tickets screen's existing empty / unauthenticated state rather than redirecting away

#### Scenario: Guest navigates to Settings after dashboard

- **WHEN** a guest user has reached at least the `'dashboard'` step
- **AND** the user chooses Settings in the FAB launcher
- **THEN** the system SHALL allow the Settings route to load
