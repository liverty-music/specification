## ADDED Requirements

### Requirement: Import ticket email route has component integration tests
The `ImportTicketEmailRoute` component SHALL have integration tests verifying multi-step wizard rendering and state transitions.

#### Scenario: Initial step renders input form
- **WHEN** the route is rendered in the initial step
- **THEN** the DOM SHALL contain the email input form

#### Scenario: Step advancement renders next step content
- **WHEN** the user completes the current step
- **THEN** the DOM SHALL transition to show the next step's content

### Requirement: Custom attribute tests use createFixture with style assertions
All custom attribute tests SHALL use `createFixture` to render the attribute on a host element and verify DOM mutations using `fixture.assertStyles()` or `fixture.assertAttr()`.

#### Scenario: tile-color attribute applies CSS custom property
- **WHEN** a `tile-color` custom attribute is rendered with a bound color value
- **THEN** `fixture.assertStyles('div', { '--tile-color': expectedColor })` SHALL pass

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
