## ADDED Requirements

### Requirement: Bottom sheet has component integration tests
The `BottomSheet` component SHALL have integration tests verifying open/close state, slot projection, and sheet-closed event.

#### Scenario: Open state renders slotted content
- **WHEN** `BottomSheet` is rendered via `createFixture` with `open.bind="true"`
- **THEN** the DOM SHALL contain the slotted content

#### Scenario: Closed state hides content
- **WHEN** `BottomSheet` is rendered with `open.bind="false"`
- **THEN** the slotted content SHALL NOT be visible in the DOM

#### Scenario: sheet-closed event fires on close
- **WHEN** the sheet transitions from open to closed
- **THEN** a `sheet-closed` custom event SHALL be dispatched

### Requirement: Coach mark has component integration tests
The `CoachMark` component SHALL have integration tests verifying phase progression, visibility state, and onTap callback.

#### Scenario: Visible state renders overlay elements
- **WHEN** the coach mark `visible` property is `true`
- **THEN** the DOM SHALL contain `.coach-mark-overlay`, `.coach-mark-tooltip`, and `.visual-spotlight` elements

#### Scenario: onTap callback is invoked
- **WHEN** the `onTargetClick` method is called
- **THEN** the bound `onTap` callback SHALL be invoked

#### Scenario: Deactivate hides all elements
- **WHEN** `deactivate()` is called
- **THEN** `visible` SHALL be `false` and the overlay SHALL be hidden

### Requirement: Celebration overlay has component integration tests
The `CelebrationOverlay` component SHALL have integration tests verifying data-state attribute, tap-to-dismiss behavior, and DOM removal.

#### Scenario: Active state sets data-state attribute
- **WHEN** the celebration overlay is rendered in active state
- **THEN** the element SHALL have `data-state="active"`

#### Scenario: Tap dispatches dismiss
- **WHEN** a pointerdown event is dispatched on the overlay
- **THEN** the overlay SHALL transition to dismissed state

### Requirement: Snack bar has component integration tests for DOM structure
The `SnackBar` component SHALL have integration tests verifying toast rendering within the snack-stack container.

#### Scenario: Toast items render inside snack-stack
- **WHEN** the snack bar service has active toasts
- **THEN** the DOM SHALL contain toast elements inside the `.snack-stack` container

#### Scenario: Toast count matches service state
- **WHEN** 3 toasts are active
- **THEN** the DOM SHALL contain exactly 3 toast elements

### Requirement: Concert highway has component integration tests
The `ConcertHighway` component SHALL have integration tests verifying stage header rendering, lane grid structure, and empty state.

#### Scenario: Three stage labels render in header
- **WHEN** `ConcertHighway` is rendered with date groups
- **THEN** the DOM SHALL contain exactly 3 stage header labels (HOME, NEAR, AWAY)

#### Scenario: Empty state renders placeholder
- **WHEN** `ConcertHighway` is rendered with empty date groups
- **THEN** the DOM SHALL contain a state-placeholder element with title and subtitle text

#### Scenario: Discover link in empty state
- **WHEN** the empty state placeholder is rendered
- **THEN** the DOM SHALL contain a link to the discover page

### Requirement: Bottom nav bar has component integration tests for active state
The `BottomNavBar` component SHALL have integration tests verifying active tab highlighting based on router state.

#### Scenario: Dashboard tab active on dashboard route
- **WHEN** the mock router reports the current path as `/dashboard`
- **THEN** the dashboard nav item SHALL have the `[data-active]` attribute

#### Scenario: All nav items render
- **WHEN** the nav bar is rendered
- **THEN** the DOM SHALL contain nav items for all configured routes

## MODIFIED Requirements

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

#### Scenario: DOM structure tests migrated from E2E to Layer 2
- **WHEN** an E2E test verifies DOM element count, text content, or attribute values without user interaction
- **THEN** the test SHALL be migrated to a Component Integration test using `createFixture`
- **AND** the E2E test SHALL be removed
