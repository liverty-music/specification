## MODIFIED Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook that checks the user's authentication state and onboarding step before allowing navigation. The hook SHALL follow a priority-based decision tree: authentication status first, then onboarding step. Routes marked as public (`auth: false`) SHALL only bypass authentication checks when they do not have a `tutorialStep` property; routes with both `auth: false` and `tutorialStep` SHALL be processed through the tutorial step logic.

#### Scenario: Public route without tutorialStep

- **WHEN** a route is configured with `data: { auth: false }` and no `tutorialStep` property
- **THEN** the system SHALL allow navigation without any authentication or tutorial checks

#### Scenario: Public route with tutorialStep during active tutorial

- **WHEN** a route is configured with `data: { auth: false, tutorialStep: N }`
- **AND** the user has `onboardingStep` between 1 and 6
- **AND** `onboardingStep >= N`
- **THEN** the system SHALL allow the route to load

#### Scenario: Public route with tutorialStep but no active tutorial

- **WHEN** a route is configured with `data: { auth: false, tutorialStep: N }`
- **AND** the user has `onboardingStep` unset or 0
- **THEN** the system SHALL redirect the user to the landing page

#### Scenario: Authenticated user navigates to any route

- **WHEN** a user has `isAuthenticated = true`
- **THEN** the system SHALL allow the route component to load regardless of `onboardingStep` value
- **AND** no tutorial UI restrictions SHALL be applied

#### Scenario: Unauthenticated user with onboardingStep in tutorial range (1-6)

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is between 1 and 6
- **THEN** the system SHALL only allow navigation to the route corresponding to the current step
- **AND** the system SHALL redirect any other navigation attempt back to the current step's route

#### Scenario: Unauthenticated user with onboardingStep = COMPLETED

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is COMPLETED (7)
- **THEN** the system SHALL redirect the user to the landing page
- **AND** the landing page SHALL display only the [Login] CTA

#### Scenario: Unauthenticated user with no onboardingStep

- **WHEN** a user has `isAuthenticated = false`
- **AND** `onboardingStep` is unset or 0
- **THEN** the system SHALL redirect the user to the landing page
- **AND** the landing page SHALL display [Get Started] and [Login]

### Requirement: Declarative Route Protection via Metadata

The system SHALL use a default-deny approach: all routes require authentication unless explicitly marked as public with `data: { auth: false }`. Tutorial routes are additionally gated by `onboardingStep`.

#### Scenario: Protected route configuration (default)

- **WHEN** a route is defined without `data: { auth: false }`
- **THEN** the `AuthHook.canLoad()` lifecycle hook SHALL enforce authentication before loading that route's component

#### Scenario: Public route configuration

- **WHEN** a route is defined with `data: { auth: false }` and no `tutorialStep` property
- **THEN** no authentication or tutorial check SHALL be performed for that route

#### Scenario: Tutorial route configuration

- **WHEN** a route is defined with `data: { auth: false, tutorialStep: N }`
- **THEN** the route SHALL be accessible without authentication only when `onboardingStep >= N`
- **AND** the route SHALL apply tutorial restrictions (coach marks, interaction locks) when `onboardingStep === N`

### Requirement: Protected Route Definitions

All routes not listed below SHALL be protected by default (no `data` annotation needed, default-deny).

The following routes SHALL be marked public with `data: { auth: false }`:
- `/` and `/welcome` (Landing Page)
- `/about` (About Page)
- `/auth/callback` (OIDC Callback)

The following routes SHALL be marked as tutorial-accessible with `data: { auth: false, tutorialStep: N }`:
- `/discover` (Artist Discovery) --- `tutorialStep: 1`
- `/dashboard` with tutorial mode --- `tutorialStep: 3` (accessible without auth during tutorial)
- `/my-artists` with tutorial mode --- `tutorialStep: 5` (accessible without auth during tutorial)

#### Scenario: Unauthenticated user at Step 1 navigates to /discover

- **WHEN** an unauthenticated user has `onboardingStep = 1`
- **AND** navigates to `/discover`
- **THEN** the system SHALL allow the route to load with tutorial restrictions active

#### Scenario: Direct URL access to /discover without tutorial

- **WHEN** an unauthenticated user with no `onboardingStep` enters `/discover` directly in the browser
- **THEN** the system SHALL redirect to the landing page (`/`)

#### Scenario: Unauthenticated user at Step 3 navigates to /dashboard

- **WHEN** an unauthenticated user has `onboardingStep = 3`
- **AND** navigates to `/dashboard`
- **THEN** the system SHALL allow the route to load with tutorial restrictions active

#### Scenario: Unauthenticated user at Step 1 navigates to /dashboard

- **WHEN** an unauthenticated user has `onboardingStep = 1`
- **AND** navigates to `/dashboard`
- **THEN** the system SHALL redirect to `/discover`

#### Scenario: Direct URL access to dashboard without authentication and no tutorial

- **WHEN** an unauthenticated user with no `onboardingStep` enters `/dashboard` directly in the browser
- **THEN** the system SHALL redirect to the landing page (`/`)

### Requirement: Auth State Readiness

The auth hook SHALL wait for the authentication service to complete its initialization before evaluating the authentication state.

#### Scenario: Page reload on protected route with valid session

- **WHEN** an authenticated user reloads the browser on a protected route
- **THEN** the system SHALL wait for the OIDC session restoration to complete
- **AND** the system SHALL allow the route to load once authenticated state is confirmed

#### Scenario: Page reload during tutorial

- **WHEN** an unauthenticated user reloads the browser during the tutorial
- **THEN** the system SHALL read `onboardingStep` from LocalStorage
- **AND** the system SHALL restore the user to the corresponding tutorial step

