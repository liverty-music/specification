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
- **WHEN** the active route path is `welcome`, `onboarding/discover`, or `auth/callback`
- **THEN** `showNav` SHALL return `false`

#### Scenario: Non-fullscreen route
- **WHEN** the active route path is `dashboard` or `about`
- **THEN** `showNav` SHALL return `true`

### Requirement: Auth hook guards all authenticated routes
The `AuthHook.canLoad` method SHALL enforce authentication on all routes except those with `data.auth === false`.

#### Scenario: Public route bypasses auth check
- **WHEN** `canLoad` is called with a route where `data.auth === false`
- **THEN** it SHALL return `true` without awaiting `authService.ready`

#### Scenario: Authenticated user on protected route
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `true`
- **THEN** it SHALL return `true`

#### Scenario: Unauthenticated user redirected to welcome
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `false`
- **THEN** it SHALL return the redirect path `/welcome`
- **AND** it SHALL show a toast notification

#### Scenario: Auth readiness is awaited before checking
- **WHEN** `canLoad` is called and `authService.ready` has not yet resolved
- **THEN** the method SHALL await `authService.ready` before checking `isAuthenticated`

### Requirement: Auth retry interceptor refreshes tokens on Unauthenticated errors
The `createAuthRetryInterceptor` SHALL intercept `Code.Unauthenticated` errors, attempt a silent OIDC token refresh, and retry the request.

#### Scenario: Silent refresh succeeds and request is retried
- **WHEN** a gRPC call returns `Code.Unauthenticated`
- **THEN** the interceptor SHALL call `signinSilent()` and retry the original request

#### Scenario: Silent refresh fails and user is redirected
- **WHEN** a gRPC call returns `Code.Unauthenticated` and `signinSilent()` throws
- **THEN** the interceptor SHALL redirect to `/welcome`

#### Scenario: Non-auth errors pass through
- **WHEN** a gRPC call returns an error code other than `Unauthenticated`
- **THEN** the interceptor SHALL re-throw the error without interception

### Requirement: Retry interceptor applies exponential backoff on transient errors
The `createRetryInterceptor` SHALL retry requests that fail with `Code.Unavailable` or `Code.DeadlineExceeded` using exponential backoff.

#### Scenario: Unavailable error triggers retry with backoff
- **WHEN** a gRPC call returns `Code.Unavailable`
- **THEN** the interceptor SHALL retry with exponential backoff delay

#### Scenario: DeadlineExceeded error triggers retry
- **WHEN** a gRPC call returns `Code.DeadlineExceeded`
- **THEN** the interceptor SHALL retry with exponential backoff delay

#### Scenario: Max retries exhausted
- **WHEN** retries are exhausted and the error persists
- **THEN** the interceptor SHALL throw the original error

#### Scenario: Non-retryable error is not retried
- **WHEN** a gRPC call returns `Code.NotFound` or `Code.InvalidArgument`
- **THEN** the interceptor SHALL throw immediately without retrying

### Requirement: Artist discovery service manages bubble state with optimistic follow
The `ArtistDiscoveryService` SHALL manage artist bubbles, track seen artists across three deduplication sets, and perform optimistic follow/unfollow with retry and rollback.

#### Scenario: Load initial artists
- **WHEN** `loadInitialArtists` is called
- **THEN** it SHALL fetch artists from the backend, convert them to bubbles, and populate `availableBubbles`

#### Scenario: Follow artist with optimistic update
- **WHEN** `followArtist` is called with an artist
- **THEN** it SHALL immediately add the artist to `followedArtists` before the backend call completes

#### Scenario: Follow fails after retry — rollback
- **WHEN** `followArtist` backend call fails and the retry also fails
- **THEN** it SHALL remove the artist from `followedArtists` (rollback)

#### Scenario: Deduplication across name, id, and mbid
- **WHEN** an artist has already been seen (by name, id, or mbid)
- **THEN** it SHALL NOT be added to `availableBubbles` again

#### Scenario: Reload with genre tag
- **WHEN** `reloadWithTag` is called with a genre tag
- **THEN** it SHALL clear existing bubbles and fetch new artists filtered by the tag

#### Scenario: Evict oldest bubbles
- **WHEN** `evictOldest` is called with count N
- **THEN** it SHALL remove the N oldest bubbles from `availableBubbles`

### Requirement: Proof service utility functions perform correct byte-to-field conversions
The proof-service pure utility functions SHALL correctly convert between byte arrays, hex strings, decimal strings, and field elements.

#### Scenario: bytesToDecimal converts big-endian bytes to decimal string
- **WHEN** `bytesToDecimal` is called with `Uint8Array([1, 0])`
- **THEN** it SHALL return `"256"`

#### Scenario: bytesToDecimal handles single zero byte
- **WHEN** `bytesToDecimal` is called with `Uint8Array([0])`
- **THEN** it SHALL return `"0"`

#### Scenario: uuidToFieldElement converts UUID to field element
- **WHEN** `uuidToFieldElement` is called with a valid UUID string
- **THEN** it SHALL return a decimal string representing the UUID's bytes as a big-endian integer

#### Scenario: bytesToHex converts bytes to hex string
- **WHEN** `bytesToHex` is called with `Uint8Array([255, 0, 171])`
- **THEN** it SHALL return `"ff00ab"`

### Requirement: Proof service verifies circuit file integrity
The `verifyCircuitIntegrity` method SHALL verify SHA-256 hashes of downloaded circuit files against hardcoded expected hashes.

#### Scenario: Hash matches expected value
- **WHEN** the SHA-256 digest of a downloaded file matches the hardcoded hash
- **THEN** verification SHALL succeed without error

#### Scenario: Hash mismatch
- **WHEN** the SHA-256 digest does not match
- **THEN** verification SHALL throw an error indicating integrity failure

### Requirement: gRPC transport injects auth headers
The `authInterceptor` within `createTransport` SHALL inject a Bearer token into every outgoing gRPC request.

#### Scenario: Authenticated user has valid token
- **WHEN** `getUserManager().getUser()` returns a user with an `access_token`
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` to the request headers

#### Scenario: No authenticated user
- **WHEN** `getUserManager().getUser()` returns `null`
- **THEN** the interceptor SHALL NOT add an Authorization header

### Requirement: Concert service forwards RPC calls with AbortSignal
The `ConcertService` SHALL forward concert listing and search requests to the backend gRPC service with AbortSignal support.

#### Scenario: List concerts by artist
- **WHEN** `listConcerts` is called with an artist ID
- **THEN** it SHALL call the backend `listConcerts` RPC and return the response

#### Scenario: List concerts by follower
- **WHEN** `listByFollower` is called
- **THEN** it SHALL call the backend `listByFollower` RPC for the authenticated user

#### Scenario: AbortSignal cancels in-flight request
- **WHEN** the provided AbortSignal is aborted during a request
- **THEN** the RPC call SHALL be cancelled

### Requirement: Error boundary service captures and sanitizes errors
The `ErrorBoundaryService` SHALL capture application errors, maintain a capped history, track breadcrumbs, and generate sanitized error reports.

#### Scenario: Capture error adds to history
- **WHEN** `captureError` is called with an error
- **THEN** the error SHALL be added to the history and set as `currentError`

#### Scenario: History is capped
- **WHEN** the error history exceeds the maximum size
- **THEN** the oldest entry SHALL be removed

#### Scenario: Sanitize redacts sensitive tokens
- **WHEN** `generateReport` is called for an error containing Bearer tokens or JWT strings
- **THEN** the report SHALL redact those tokens

#### Scenario: GitHub issue URL is constructed correctly
- **WHEN** `buildGitHubIssueUrl` is called
- **THEN** it SHALL return a valid GitHub URL with pre-filled title and body

#### Scenario: Dismiss clears current error
- **WHEN** `dismiss` is called
- **THEN** `currentError` SHALL be set to `null`

### Requirement: Dashboard route manages stale data on reload failure
The `Dashboard` route SHALL preserve existing data and mark it as stale when a data reload fails.

#### Scenario: Successful data load
- **WHEN** `loadData` succeeds
- **THEN** `groupedEvents` SHALL contain the returned date groups and `isStale` SHALL be `false`

#### Scenario: Reload failure preserves old data
- **WHEN** `loadData` fails after a previous successful load
- **THEN** `groupedEvents` SHALL retain the previous data and `isStale` SHALL be `true`

#### Scenario: AbortError is ignored
- **WHEN** `loadData` throws an AbortError (navigation-triggered)
- **THEN** the error SHALL NOT be set on the component

#### Scenario: Retry clears error and reloads
- **WHEN** `retry` is called
- **THEN** the error state SHALL be cleared and `loadData` SHALL be invoked again

### Requirement: Discover page debounces search with stale response guard
The `DiscoverPage` route SHALL debounce artist search input by 300ms and discard stale responses.

#### Scenario: Search is debounced
- **WHEN** the search query changes
- **THEN** `performSearch` SHALL NOT be called until 300ms after the last change

#### Scenario: Stale search response is discarded
- **WHEN** the search query changes again before a previous search responds
- **THEN** the previous response SHALL be discarded

#### Scenario: Genre tag toggle activates and deactivates
- **WHEN** a genre tag is selected and then selected again
- **THEN** the first selection SHALL call `reloadWithTag` and the second SHALL call `loadInitialArtists`

#### Scenario: Clear search restores bubble view
- **WHEN** `clearSearch` is called
- **THEN** the search query SHALL be emptied and the bubble canvas SHALL resume

### Requirement: Artist discovery page dismisses guidance overlay
The `ArtistDiscoveryPage` route SHALL auto-dismiss the guidance overlay after 5 seconds with a 400ms fade animation.

#### Scenario: Guidance auto-dismiss after 5 seconds
- **WHEN** the component is attached
- **THEN** the guidance overlay SHALL become hidden after 5000ms

#### Scenario: Fade animation before removal
- **WHEN** the guidance overlay begins dismissing
- **THEN** a 400ms fade-out animation SHALL complete before the element is removed

#### Scenario: Artist selection triggers follow and live event check
- **WHEN** an artist is selected
- **THEN** `followArtist` SHALL be called followed by `checkLiveEvents`

### Requirement: Tickets page generates ZK proof entry QR codes
The `TicketsPage` route SHALL generate ZK proof entry codes and display them as QR code images.

#### Scenario: Successful proof generation
- **WHEN** `generateEntryCode` is called for a ticket
- **THEN** it SHALL call `ProofService.generateEntryProof`, encode the result as base64 JSON, generate a QR code, and open the QR modal

#### Scenario: Proof generation error
- **WHEN** `generateEntryProof` throws an error
- **THEN** the error SHALL be captured and displayed

#### Scenario: AbortError is silently ignored
- **WHEN** proof generation is aborted due to navigation
- **THEN** no error SHALL be shown

#### Scenario: mintDate and formatTokenId are pure formatters
- **WHEN** `mintDate` is called with a timestamp
- **THEN** it SHALL return a formatted date string
- **WHEN** `formatTokenId` is called with a token ID
- **THEN** it SHALL return a shortened display format

### Requirement: Event detail sheet computes URLs and handles touch dismiss
The `EventDetailSheet` component SHALL compute Google Maps and Calendar URLs and support touch drag-to-dismiss with a 100px threshold.

#### Scenario: Google Maps URL construction
- **WHEN** the sheet is opened with an event that has a venue name
- **THEN** `googleMapsUrl` SHALL return a valid Google Maps search URL for the venue

#### Scenario: Google Calendar URL construction
- **WHEN** the sheet is opened with an event
- **THEN** `calendarUrl` SHALL return a Google Calendar URL with correct start and end times

#### Scenario: Touch drag exceeding threshold closes sheet
- **WHEN** a touch drag moves more than 100px downward
- **THEN** the sheet SHALL close

#### Scenario: Touch drag below threshold keeps sheet open
- **WHEN** a touch drag moves less than 100px
- **THEN** the sheet SHALL remain open

### Requirement: Test mock helpers cover all tested DI interfaces
The test helper library SHALL provide typed mock factories for all DI interfaces used across the test suite.

#### Scenario: Mock router factory
- **WHEN** `createMockRouter` is called
- **THEN** it SHALL return a `Partial<IRouter>` with `load` as a Vitest spy

#### Scenario: Mock toast service factory
- **WHEN** `createMockToastService` is called
- **THEN** it SHALL return a `Partial<IToastService>` with `show` as a Vitest spy

#### Scenario: Mock error boundary factory
- **WHEN** `createMockErrorBoundary` is called
- **THEN** it SHALL return a `Partial<IErrorBoundaryService>` with `captureError` and `dismiss` as Vitest spies

### Requirement: Timer cleanup uses afterEach unconditionally
All tests that use `vi.useFakeTimers()` SHALL restore real timers in `afterEach`, never inside individual `it()` blocks.

#### Scenario: Fake timers restored after each test
- **WHEN** a test suite uses `vi.useFakeTimers()` in `beforeEach`
- **THEN** `vi.useRealTimers()` SHALL be called in `afterEach`

#### Scenario: Mocks restored after each test
- **WHEN** a test suite uses mock spies
- **THEN** `vi.restoreAllMocks()` SHALL be called in `afterEach`

#### Scenario: Fixture tests use stop(true) in afterEach
- **WHEN** a test suite creates fixtures
- **THEN** each fixture SHALL be stopped via `stop(true)` in `afterEach` or at the end of each test

### Requirement: Coverage reporting is configured
Vitest SHALL be configured with V8 coverage reporting with raised thresholds reflecting the expanded test suite.

#### Scenario: Running tests with coverage
- **WHEN** `vitest --coverage` is executed
- **THEN** a coverage report SHALL be generated showing statement, branch, and function coverage

#### Scenario: Coverage thresholds enforce minimum levels
- **WHEN** coverage falls below thresholds (statements: 65%, branches: 75%, functions: 65%, lines: 65%)
- **THEN** the coverage check SHALL fail

#### Scenario: Dead config patterns are removed
- **WHEN** vitest coverage exclusion patterns are evaluated
- **THEN** the pattern `src/*-page.ts` SHALL NOT be present (it matches no files)

#### Scenario: auth-service.ts is included in coverage
- **WHEN** vitest coverage exclusion patterns are evaluated
- **THEN** `src/services/auth-service.ts` SHALL NOT be excluded (lazy init refactor enables coverage)

### Requirement: Global fixture cleanup awaits all stop() calls
The `test/setup.ts` afterEach hook SHALL properly await fixture cleanup using `Promise.all` instead of `forEach(async)`.

#### Scenario: Fixture cleanup completes before next test
- **WHEN** a test creates one or more fixtures via `createFixture`
- **THEN** the global `afterEach` hook SHALL await `Promise.all(fixtures.map(f => f.stop(true).catch(() => {})))` before clearing the fixtures array

#### Scenario: Cleanup errors do not fail the test
- **WHEN** a fixture's `stop(true)` throws an error during cleanup
- **THEN** the error SHALL be caught silently and other fixtures SHALL still be cleaned up

### Requirement: All afterEach hooks prevent test state pollution
All test suites SHALL include proper cleanup in `afterEach` to prevent state leaking between tests.

#### Scenario: localStorage is cleared after tests that use it
- **WHEN** a test suite reads or writes `localStorage`
- **THEN** `localStorage.clear()` SHALL be called in `afterEach`

### Requirement: Mock helpers return typed Partial interfaces
All mock factory functions in `test/helpers/mock-*.ts` SHALL return explicitly typed `Partial<IInterface>` with all method properties as `vi.fn()` spies.

#### Scenario: mock-i18n returns typed interface
- **WHEN** `createMockI18n()` is called
- **THEN** it SHALL return `Partial<I18N>` with explicit return type annotation

#### Scenario: mock-toast returns typed interface
- **WHEN** `createMockToast()` is called
- **THEN** it SHALL return a properly typed mock with explicit return type annotation

#### Scenario: mock-error-boundary has all properties as spies or typed values
- **WHEN** `createMockErrorBoundary()` is called
- **THEN** `currentError` and `errorHistory` SHALL be properly typed (not plain `null`/`[]` without type context)

### Requirement: No deprecated Aurelia testing APIs are used
All test files SHALL use `stop(true)` instead of the deprecated `tearDown()` method.

#### Scenario: Smoke tests use stop(true)
- **WHEN** `test/smoke/component-compile.spec.ts` cleans up fixtures
- **THEN** it SHALL call `stop(true)` instead of `tearDown()`

#### Scenario: No tearDown() calls exist in the codebase
- **WHEN** the test codebase is searched for `tearDown`
- **THEN** zero usages SHALL be found (excluding comments and type imports)

### Requirement: Component integration tests use createFixture with official assertion helpers
Component integration tests SHALL use `createFixture` (fluent builder API) from `@aurelia/testing` and verify DOM output using the official fixture assertion methods. Components that depend on browser APIs unavailable in JSDOM (e.g., popover, showModal, Canvas) SHALL use DI Unit tests instead.

#### Scenario: Fixture test verifies template binding
- **WHEN** a component integration test is created for a component with bindable properties
- **THEN** the test SHALL use `createFixture.component(X).html(Y).deps(Z).build().started` and verify rendered output with `fixture.assertText()` or `fixture.assertAttr()`

#### Scenario: Fixture test uses trigger for user interaction (when applicable)
- **WHEN** a component integration test verifies click or keyboard interaction on a component whose template does not require browser-only APIs (popover, dialog, canvas)
- **THEN** the test SHALL use `fixture.trigger.click(selector)` or `fixture.trigger.keydown(selector, init)` instead of manually dispatching events

#### Scenario: Fixture test uses type() for input simulation (when applicable)
- **WHEN** a component integration test verifies text input binding on a component whose template does not require browser-only APIs
- **THEN** the test SHALL use `fixture.type(selector, value)` which sets the value and dispatches an input event to trigger two-way binding

#### Scenario: Fixture test awaits tasksSettled() after state mutation (when applicable)
- **WHEN** a fixture test mutates component state and then asserts DOM output
- **THEN** the test SHALL call `await tasksSettled()` between the mutation and the assertion

#### Scenario: Fixture test uses stop(true) for cleanup
- **WHEN** a component integration test completes
- **THEN** the test SHALL call `await fixture.stop(true)` (not the deprecated `tearDown()`) for proper cleanup

#### Scenario: Components with JSDOM-incompatible APIs use DI Unit tests
- **WHEN** a component depends on popover API, showModal, HTMLCanvasElement.getContext, or other browser-only APIs
- **THEN** the component SHALL be tested via DI Unit pattern (`createTestContainer` + `Registration.instance`) instead of `createFixture`

### Requirement: Smoke tests use meaningful DOM assertions
Smoke tests in `test/smoke/component-compile.spec.ts` SHALL replace tautological assertions with meaningful DOM verification using fixture assertion methods.

#### Scenario: Smoke test verifies rendered element exists
- **WHEN** a smoke test renders a component via `createFixture`
- **THEN** it SHALL verify the component's root element exists using `fixture.getBy()` or `fixture.queryBy()` instead of `expect(true).toBe(true)`

#### Scenario: Smoke test verifies basic attribute or text content
- **WHEN** a smoke test renders a component with known default state
- **THEN** it SHALL verify at least one meaningful attribute or text content using `fixture.assertAttr()` or `fixture.assertText()`

### Requirement: Bottom nav bar has component integration tests
The `BottomNavBar` component SHALL have integration tests verifying navigation item rendering and active state.

#### Scenario: Nav items render for all routes
- **WHEN** `BottomNavBar` is rendered via `createFixture`
- **THEN** the DOM SHALL contain navigation items for all configured routes

#### Scenario: Active route is highlighted
- **WHEN** the router reports the current path as `/dashboard`
- **THEN** the dashboard nav item SHALL have the active CSS class

### Requirement: Snack bar service logic is tested
The `SnackBar` component depends on the popover API (`showPopover`/`hidePopover`) which is not available in JSDOM. Service-level snack bar logic (event aggregation, toast lifecycle, auto-dismiss timing) SHALL be tested via DI Unit tests. DOM behavior SHALL be verified by E2E tests.

#### Scenario: Snack events are aggregated and shown
- **WHEN** a `Snack` event is published via `IEventAggregator`
- **THEN** the snack bar service SHALL add the message to its internal queue (tested in `test/services/snack-bar.spec.ts`)

#### Scenario: Auto-dismiss fires after configured duration
- **WHEN** a snack is shown with a configured `durationMs`
- **THEN** the service SHALL schedule dismissal after the duration (tested in `test/services/snack-bar.spec.ts`)

### Requirement: User home selector has component integration tests
The `UserHomeSelector` component SHALL have integration tests verifying region/prefecture selection and persistence.

#### Scenario: Region options are rendered
- **WHEN** the selector is rendered
- **THEN** the DOM SHALL contain selectable region options

#### Scenario: Selection persists via service call
- **WHEN** a user selects a region and prefecture
- **THEN** the component SHALL call the user service to persist the selection

### Requirement: Post-signup dialog has component integration tests
The `PostSignupDialog` component SHALL have integration tests verifying the multi-step post-signup flow.

#### Scenario: Dialog renders notification prompt step
- **WHEN** the dialog is opened after signup
- **THEN** the DOM SHALL display the notification permission prompt

#### Scenario: Dialog advances to PWA install step
- **WHEN** the user completes the notification step
- **THEN** the dialog SHALL advance to the PWA install prompt step

### Requirement: Error banner has component integration tests
The `ErrorBanner` component SHALL have integration tests verifying error display, GitHub issue URL, and dismiss behavior.

#### Scenario: Error message is displayed
- **WHEN** the error boundary service has a current error
- **THEN** the banner DOM SHALL display the error message

#### Scenario: Dismiss clears the error
- **WHEN** the user clicks the dismiss button
- **THEN** the error boundary service's `dismiss()` method SHALL be called

### Requirement: Settings route has component integration tests
The `SettingsRoute` component SHALL have integration tests verifying conditional section rendering and language selection.

#### Scenario: Language options are rendered via repeat.for
- **WHEN** the settings route is rendered via `createFixture`
- **THEN** the DOM SHALL contain language option elements for all configured locales

#### Scenario: Email verification status is displayed conditionally
- **WHEN** the user has a verified email
- **THEN** the verified status indicator SHALL be visible and the verify button SHALL NOT be rendered

#### Scenario: PWA install section shown only when installable
- **WHEN** the PWA install service reports `canShow: true`
- **THEN** the install section SHALL be visible in the DOM

### Requirement: Import ticket email route has component integration tests
The `ImportTicketEmailRoute` component SHALL have integration tests verifying multi-step wizard rendering and state transitions.

#### Scenario: Initial step renders input form
- **WHEN** the route is rendered in the initial step
- **THEN** the DOM SHALL contain the email input form

#### Scenario: Step advancement renders next step content
- **WHEN** the user completes the current step
- **THEN** the DOM SHALL transition to show the next step's content

### Requirement: Concert highway CE has component integration tests
The `ConcertHighway` component (extracted from dashboard-route) SHALL have integration tests verifying bindable rendering, beam index mapping, and lifecycle cleanup.

#### Scenario: Date groups render lane grid
- **WHEN** `ConcertHighway` is rendered via `createFixture` with dateGroups containing home/nearby/away events
- **THEN** the DOM SHALL contain date header elements and event cards in three lane columns

#### Scenario: Beam index map is built from matched events
- **WHEN** dateGroups contain events with `matched: true`
- **THEN** `beamIndexMap` SHALL contain entries for each matched event ID

#### Scenario: Readonly mode disables interaction
- **WHEN** `isReadonly` is set to `true`
- **THEN** event cards SHALL NOT dispatch event-selected on click

#### Scenario: Detaching cleans up scroll listener and cancels rAF
- **WHEN** `detaching()` is called
- **THEN** the scroll event listener SHALL be removed and any pending `requestAnimationFrame` SHALL be cancelled

### Requirement: Welcome route has component integration tests
The `WelcomeRoute` component SHALL have integration tests verifying auth guard behavior, preview data loading, language switching, and navigation.

#### Scenario: Unauthenticated user sees welcome content
- **WHEN** the welcome route is rendered with an unauthenticated auth mock
- **THEN** the rendered DOM SHALL contain sign-in and sign-up call-to-action elements

#### Scenario: canLoad redirects authenticated users
- **WHEN** `canLoad` is called with an authenticated auth service mock
- **THEN** it SHALL return a redirect path to the dashboard

#### Scenario: Preview concert data loads on attached
- **WHEN** the welcome route is attached
- **THEN** it SHALL call `concertService.listWithProximity` and populate `dateGroups`

#### Scenario: Language switching updates locale via @observable
- **WHEN** `currentLocale` changes
- **THEN** the `currentLocaleChanged` handler SHALL call `changeLocale` with the new locale

### Requirement: Custom attribute tests use createFixture with style verification
All custom attribute tests SHALL use `createFixture` to render the attribute on a host element and verify DOM mutations using `fixture.getBy()` + `style.getPropertyValue()` for CSS custom properties (JSDOM does not expose custom properties via `getComputedStyle()`).

#### Scenario: tile-color attribute applies CSS custom property
- **WHEN** a `tile-color` custom attribute is rendered with a bound color value
- **THEN** `fixture.getBy('div').style.getPropertyValue('--_tile-color')` SHALL return the expected color value

### Requirement: Value converter tests include fixture integration tests
Value converter test suites SHALL include at least one `createFixture` integration test verifying the converter works within an Aurelia view pipeline.

#### Scenario: Date converter renders correctly in template
- **WHEN** `createFixture` renders `${date | date}` with a known date value
- **THEN** `fixture.assertText()` SHALL contain the expected formatted date string
