## ADDED Requirements

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

#### Scenario: Fake timers are restored in afterEach, not inside it()
- **WHEN** a test suite uses `vi.useFakeTimers()`
- **THEN** `vi.useRealTimers()` SHALL be called in `afterEach`, never inside individual `it()` blocks

#### Scenario: Mock spies are restored in afterEach
- **WHEN** a test suite creates mock spies
- **THEN** `vi.restoreAllMocks()` SHALL be called in `afterEach`

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

### Requirement: Custom attribute tests use createFixture with style assertions
All custom attribute tests SHALL use `createFixture` to render the attribute on a host element and verify DOM mutations using `fixture.assertStyles()` or `fixture.assertAttr()`.

#### Scenario: tile-color attribute applies CSS custom property
- **WHEN** a `tile-color` custom attribute is rendered with a bound color value
- **THEN** `fixture.assertStyles('div', { '--tile-color': expectedColor })` SHALL pass

### Requirement: Value converter tests include fixture integration tests
Value converter test suites SHALL include at least one `createFixture` integration test verifying the converter works within an Aurelia view pipeline.

#### Scenario: Date converter renders correctly in template
- **WHEN** `createFixture` renders `${date | dateFormat}` with a known date value
- **THEN** `fixture.assertText()` SHALL contain the expected formatted date string

## MODIFIED Requirements

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
