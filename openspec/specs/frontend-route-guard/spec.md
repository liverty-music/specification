## Requirements

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

## Test Cases

### Unit Tests (Vitest)

#### TC-RG-01: Onboarding user navigating to route without tutorialStep redirects silently

- **Given** `isAuthenticated = false`, `onboardingStep = 1`
- **When** navigating to a route without `data.tutorialStep` (e.g., Tickets)
- **Then** AuthHook SHALL return a redirect to the current step's route
- **And** no "Login required" toast SHALL be published to EventAggregator

#### TC-RG-02: Onboarding user navigating to future step redirects to current step

- **Given** `isAuthenticated = false`, `onboardingStep = 1`
- **When** navigating to a route with `data.tutorialStep = 3`
- **Then** AuthHook SHALL redirect to the Step 1 route (discover)
- **And** no toast SHALL be published

#### TC-RG-03: Non-onboarding unauthenticated user sees "Login required" toast

- **Given** `isAuthenticated = false`, `onboardingStep = 0` (or unset)
- **When** navigating to a protected route
- **Then** AuthHook SHALL redirect to the landing page
- **And** a "Login required" toast SHALL be published to EventAggregator

#### TC-RG-04: Authenticated user passes through without restriction

- **Given** `isAuthenticated = true`
- **When** navigating to any route
- **Then** AuthHook SHALL allow navigation (return `true`)

#### TC-RG-05: Discovery-step user with readyForDashboard=true navigates to dashboard — allowed + step advanced

- **Given** `isAuthenticated = false`, `onboardingStep = 'discovery'`, `readyForDashboard = true`
- **When** navigating to `/dashboard`
- **Then** AuthHook SHALL return `true`
- **And** `onboarding.setStep('dashboard')` SHALL be called

#### TC-RG-06: Discovery-step user with readyForDashboard=false navigates to dashboard — redirected

- **Given** `isAuthenticated = false`, `onboardingStep = 'discovery'`, `readyForDashboard = false`
- **When** navigating to `/dashboard`
- **Then** AuthHook SHALL return a redirect to `/discovery`
- **And** no step advancement SHALL occur

#### TC-RG-07: readyForDashboard is true when follow count threshold is met

- **Given** `onboardingStep = 'discovery'`
- **And** `followedCount = 5` (≥ DASHBOARD_FOLLOW_TARGET)
- **When** `OnboardingService.readyForDashboard` is evaluated
- **Then** it SHALL return `true`

#### TC-RG-08: readyForDashboard is true when concert artist threshold is met

- **Given** `onboardingStep = 'discovery'`
- **And** `artistsWithConcertsCount = 3` (≥ DASHBOARD_CONCERT_TARGET)
- **When** `OnboardingService.readyForDashboard` is evaluated
- **Then** it SHALL return `true`

#### TC-RG-09: readyForDashboard is false when both counts are below threshold

- **Given** `onboardingStep = 'discovery'`
- **And** `followedCount < 5` AND `artistsWithConcertsCount < 3`
- **When** `OnboardingService.readyForDashboard` is evaluated
- **Then** it SHALL return `false`

#### TC-RG-10: readyForDashboard is false when step is not discovery

- **Given** `onboardingStep` is any value other than `'discovery'`
- **And** `followedCount` and `artistsWithConcertsCount` exceed their respective thresholds
- **When** `OnboardingService.readyForDashboard` is evaluated
- **Then** it SHALL return `false`
