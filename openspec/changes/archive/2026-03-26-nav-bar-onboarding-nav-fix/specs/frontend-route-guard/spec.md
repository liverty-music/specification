## MODIFIED Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook that checks the user's authentication state and onboarding step before allowing navigation. The hook SHALL follow a priority-based decision tree: authentication status first, then onboarding step, with an onboarding-aware fallback for routes without tutorial step metadata.

#### Scenario: Authenticated user navigates to any route

- **WHEN** a user has `isAuthenticated = true`
- **THEN** the system SHALL allow the route component to load regardless of `onboardingStep` value
- **AND** no tutorial UI restrictions SHALL be applied

#### Scenario: Unauthenticated user with onboardingStep in tutorial range navigates to a tutorial-gated route

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **AND** the target route has `data.tutorialStep` defined
- **THEN** the system SHALL allow navigation if `onboardingStep >= tutorialStep`
- **AND** the system SHALL redirect to the current step's route if `onboardingStep < tutorialStep`

#### Scenario: Unauthenticated user in onboarding navigates to a route without tutorialStep

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **AND** the target route does NOT have `data.tutorialStep` defined
- **AND** the target route does NOT have `data.auth = false`
- **THEN** the system SHALL redirect to the route corresponding to the current onboarding step
- **AND** the system SHALL NOT display a "Login required" toast
- **AND** the system SHALL NOT display any error notification

#### Scenario: Unauthenticated discovery-step user who has met the progression condition navigates to dashboard

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is `'discovery'`
- **AND** `OnboardingService.readyForDashboard` is `true` (≥5 followed artists OR ≥3 artists with concerts)
- **AND** the user navigates to the `/dashboard` route (e.g., via the nav bar)
- **THEN** the system SHALL allow the navigation to proceed
- **AND** the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** no redirect or toast SHALL be shown

#### Scenario: Unauthenticated discovery-step user who has NOT met the progression condition navigates to dashboard

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is `'discovery'`
- **AND** `OnboardingService.readyForDashboard` is `false`
- **AND** the user navigates to the `/dashboard` route
- **THEN** the system SHALL redirect the user back to `/discovery`
- **AND** no toast SHALL be shown

#### Scenario: Unauthenticated user with onboardingStep = COMPLETED

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is COMPLETED (7)
- **THEN** the system SHALL redirect the user to the landing page
- **AND** the landing page SHALL display only the [Login] CTA

#### Scenario: Unauthenticated user with no onboardingStep

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is unset or 0
- **THEN** the system SHALL redirect the user to the landing page
- **AND** the system SHALL display a "Login required" toast notification
- **AND** the landing page SHALL display [Get Started] and [Login]

## ADDED Requirements

### Requirement: Onboarding Dashboard Readiness

`OnboardingService` SHALL expose a `readyForDashboard` computed property that encapsulates the dashboard-unlock condition for unauthenticated users in the discovery step.

#### Scenario: readyForDashboard is true when follow count threshold is met

- **WHEN** `onboardingStep` is `'discovery'`
- **AND** the followed artist count is ≥5
- **THEN** `OnboardingService.readyForDashboard` SHALL return `true`

#### Scenario: readyForDashboard is true when concert artist threshold is met

- **WHEN** `onboardingStep` is `'discovery'`
- **AND** the count of followed artists with at least one concert is ≥3
- **THEN** `OnboardingService.readyForDashboard` SHALL return `true`

#### Scenario: readyForDashboard is false before thresholds are met

- **WHEN** `onboardingStep` is `'discovery'`
- **AND** followed artist count is <5
- **AND** artists-with-concerts count is <3
- **THEN** `OnboardingService.readyForDashboard` SHALL return `false`

#### Scenario: readyForDashboard is false outside the discovery step

- **WHEN** `onboardingStep` is any value other than `'discovery'`
- **THEN** `OnboardingService.readyForDashboard` SHALL return `false`
