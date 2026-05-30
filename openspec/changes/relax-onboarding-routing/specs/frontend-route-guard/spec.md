## MODIFIED Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook that checks the user's authentication state and onboarding step before allowing navigation. The hook SHALL follow a priority-based decision tree: authentication status first, then onboarding step, with an onboarding-aware fallback for routes without tutorial step metadata. When the hook redirects a user away from a route they attempted to reach during onboarding, it SHALL surface contextual feedback (a snackbar or a re-lit coach mark) — no guard-initiated redirect during onboarding SHALL be a silent no-op.

#### Scenario: Authenticated user navigates to any route

- **WHEN** a user has `isAuthenticated = true`
- **THEN** the system SHALL allow the route component to load regardless of `onboardingStep` value
- **AND** no tutorial UI restrictions SHALL be applied

#### Scenario: Unauthenticated user with onboardingStep in tutorial range navigates to a tutorial-gated route

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **AND** the target route has `data.tutorialStep` defined
- **THEN** the system SHALL allow navigation if `onboardingStep >= tutorialStep`
- **AND** if `onboardingStep < tutorialStep`, the system SHALL redirect to the current step's route AND publish a contextual snackbar explaining what is required to unlock the target

#### Scenario: Unauthenticated user in onboarding navigates to a route without tutorialStep

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **AND** the target route does NOT have `data.tutorialStep` defined
- **AND** the target route does NOT have `data.auth = false`
- **AND** the target route is NOT an explicitly early-unlocked route (see "Settings reachable during onboarding")
- **THEN** the system SHALL redirect to the route corresponding to the current onboarding step
- **AND** the system SHALL publish a contextual snackbar indicating why the destination is not yet available

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
- **AND** the system SHALL publish a contextual snackbar (e.g. "あと N 組フォローでタイムテーブルが見られます", where N = `DASHBOARD_FOLLOW_TARGET - followedCount`) or re-light the dashboard coach mark

#### Scenario: Unauthenticated user with onboardingStep = COMPLETED

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is COMPLETED (7)
- **THEN** the system SHALL allow navigation to any application route (free roam)
- **AND** the system SHALL NOT force a redirect to the landing page
- **AND** account-only features on each destination SHALL be hidden at point of use rather than blocked (per `guest-mode-access`)

#### Scenario: Unauthenticated user with no onboardingStep

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is unset or 0
- **THEN** the system SHALL redirect the user to the landing page
- **AND** the system SHALL display a "Login required" toast notification
- **AND** the landing page SHALL display [Get Started] and [Login]

## ADDED Requirements

### Requirement: Settings Reachable During Onboarding

The system SHALL allow an unauthenticated user to navigate to the Settings route from the `'discovery'` step onward, regardless of `tutorialStep` ordering, so that the sign-in / sign-up and language affordances are reachable early.

#### Scenario: Discovery-step guest opens Settings

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is `'discovery'` or later (but not COMPLETED)
- **AND** the user navigates to `/settings`
- **THEN** the system SHALL allow the Settings route to load
- **AND** the system SHALL NOT redirect back to the current onboarding step

### Requirement: Welcome Reachable During Onboarding

The system SHALL allow an unauthenticated user in onboarding to navigate back to the Welcome (landing) route to re-read the value proposition, without being bounced forward to the current onboarding step.

#### Scenario: Onboarding guest returns to Welcome

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **AND** the user navigates to `/` (Welcome)
- **THEN** the system SHALL allow the Welcome route to load
- **AND** merely viewing Welcome SHALL NOT reset `onboardingStep`
- **AND** `onboardingStep` SHALL change only if the user explicitly taps [Get Started]
