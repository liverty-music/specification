# Frontend Testing

## Purpose

Establish comprehensive test coverage for the Aurelia 2 frontend application, including test infrastructure, service tests, component tests, and coverage reporting.

This capability ensures code quality, prevents regressions, and enables confident refactoring through automated testing.

## Requirements

### Requirement: Test infrastructure provides shared mock factories
The test suite SHALL provide reusable mock factories for commonly used DI dependencies (`ILogger`, `IAuthService`, `IRouter`, RPC service clients) in `test/helpers/`.

#### Scenario: Creating a mock logger
- **WHEN** a test imports `createMockLogger` from `test/helpers/mock-logger`
- **THEN** it SHALL return an object implementing `ILogger` with all methods as Vitest spies (`debug`, `info`, `warn`, `error`, `scopeTo`)

#### Scenario: Creating a mock auth service
- **WHEN** a test imports `createMockAuth` from `test/helpers/mock-auth`
- **THEN** it SHALL return an object implementing `IAuthService` with configurable `isAuthenticated`, `user`, and spy methods for `signIn`, `signOut`, `signUp`, `handleCallback`

#### Scenario: Creating a test DI container
- **WHEN** a test calls `createTestContainer` with mock registrations
- **THEN** it SHALL return an Aurelia `IContainer` with the provided mocks registered and `ILogger` pre-registered

### Requirement: Color generator produces deterministic colors
The `artistColor` function SHALL produce a valid HSL color string deterministically from any input string.

#### Scenario: Same input produces same color
- **WHEN** `artistColor` is called twice with the same artist name
- **THEN** both calls SHALL return identical HSL color strings

#### Scenario: Different inputs produce different colors
- **WHEN** `artistColor` is called with different artist names
- **THEN** the returned HSL hue values SHALL differ

#### Scenario: Empty string input
- **WHEN** `artistColor` is called with an empty string
- **THEN** it SHALL return a valid HSL color string without throwing

### Requirement: Dashboard service groups concerts by date
The `DashboardService.loadDashboardEvents` method SHALL fetch followed artists, retrieve concerts for each artist in parallel, convert them to `LiveEvent` objects, and group them by date.

#### Scenario: Multiple artists with concerts
- **WHEN** the user follows 2 artists and each has concerts on different dates
- **THEN** the returned `DateGroup[]` SHALL contain entries sorted by date, each containing the corresponding `LiveEvent` objects

#### Scenario: No followed artists
- **WHEN** the user follows no artists
- **THEN** `loadDashboardEvents` SHALL return an empty `DateGroup[]`

#### Scenario: RPC call failure for one artist
- **WHEN** concert fetching fails for one artist but succeeds for another
- **THEN** the service SHALL return events from the successful artist (using `Promise.allSettled` resilience)

### Requirement: Loading sequence service orchestrates data aggregation
The `LoadingSequenceService.aggregateData` method SHALL fetch followed artists (with retry), search concerts in batches, and enforce timeout and minimum display constraints.

#### Scenario: Successful aggregation
- **WHEN** `aggregateData` is called and all RPC calls succeed
- **THEN** it SHALL complete after at least MINIMUM_DISPLAY_MS (3000ms)

#### Scenario: Artist fetch retry on failure
- **WHEN** the first call to list followed artists fails
- **THEN** the service SHALL retry once before giving up

#### Scenario: Concert search batching
- **WHEN** the user follows more than BATCH_SIZE (5) artists
- **THEN** concert searches SHALL be executed in batches of BATCH_SIZE

#### Scenario: Global timeout
- **WHEN** data aggregation exceeds GLOBAL_TIMEOUT_MS (10000ms)
- **THEN** the operation SHALL abort via AbortSignal

### Requirement: Onboarding service routes based on completion status
The `OnboardingService` SHALL check whether the user has completed onboarding and redirect to the appropriate route.

#### Scenario: User has completed onboarding
- **WHEN** `hasCompletedOnboarding` is called and the user has at least one followed artist
- **THEN** it SHALL return `true`

#### Scenario: User has not completed onboarding
- **WHEN** `hasCompletedOnboarding` is called and the user has no followed artists
- **THEN** it SHALL return `false`

#### Scenario: Redirect authenticated user with completed onboarding
- **WHEN** `redirectBasedOnStatus` is called for an authenticated user who has completed onboarding
- **THEN** the router SHALL navigate to `dashboard`

#### Scenario: Redirect authenticated user without onboarding
- **WHEN** `redirectBasedOnStatus` is called for an authenticated user who has not completed onboarding
- **THEN** the router SHALL navigate to `onboarding/discover`

### Requirement: Toast notification service manages toast lifecycle
The `ToastNotification.show` method SHALL add a toast, animate it visible, auto-dismiss after the specified duration, and remove it after the exit animation.

#### Scenario: Show a toast
- **WHEN** `show` is called with a message
- **THEN** a toast item SHALL be added to `toasts` array and become `visible` after the next animation frame

#### Scenario: Auto-dismiss after duration
- **WHEN** `durationMs` elapses after showing a toast
- **THEN** the toast `visible` SHALL be set to `false`

#### Scenario: Remove after exit animation
- **WHEN** 400ms elapses after a toast is dismissed
- **THEN** the toast SHALL be removed from the `toasts` array

### Requirement: Event card computes display properties
The `EventCard` component SHALL compute background color from artist name and format dates in Japanese locale.

#### Scenario: Background color from artist name
- **WHEN** an `EventCard` is rendered with an event
- **THEN** `backgroundColor` SHALL return the HSL color from `artistColor(event.artistName)`

#### Scenario: Click dispatches event-selected
- **WHEN** the user clicks the event card
- **THEN** a bubbling `CustomEvent` named `event-selected` SHALL be dispatched with `{ event }` in `detail`

### Requirement: Live highway displays grouped events
The `LiveHighway` component SHALL render date groups and delegate event selection.

#### Scenario: Empty state
- **WHEN** `dateGroups` is an empty array
- **THEN** `isEmpty` SHALL return `true`

#### Scenario: Event selection delegation
- **WHEN** `onEventSelected` is called with a custom event containing a `LiveEvent`
- **THEN** it SHALL call `detailSheet.open` with that event

### Requirement: Auth status delegates to auth service
The `AuthStatus` component SHALL delegate sign-in, sign-up, and sign-out actions to `IAuthService`.

#### Scenario: Sign in
- **WHEN** `signIn` is called
- **THEN** it SHALL call `auth.signIn()`

#### Scenario: Sign up
- **WHEN** `signUp` is called
- **THEN** it SHALL call `auth.signUp()`

#### Scenario: Sign out
- **WHEN** `signOut` is called
- **THEN** it SHALL call `auth.signOut()`

### Requirement: MyApp showNav hides navigation on fullscreen routes
The `MyApp.showNav` getter SHALL return `false` for fullscreen routes and `true` for other routes.

#### Scenario: Fullscreen route
- **WHEN** the active route path is `welcome`, `onboarding/discover`, `onboarding/loading`, or `auth/callback`
- **THEN** `showNav` SHALL return `false`

#### Scenario: Non-fullscreen route
- **WHEN** the active route path is `dashboard` or `about`
- **THEN** `showNav` SHALL return `true`

### Requirement: Coverage reporting is configured
Vitest SHALL be configured with V8 coverage reporting.

#### Scenario: Running tests with coverage
- **WHEN** `vitest --coverage` is executed
- **THEN** a coverage report SHALL be generated showing statement, branch, and function coverage
