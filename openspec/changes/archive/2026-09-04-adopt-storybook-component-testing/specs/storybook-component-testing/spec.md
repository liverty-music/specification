## Purpose

Establish Storybook as the isolated development surface and CI-enforced test harness for the Aurelia 2 frontend's presentational components, covering story authoring scope, browser-mode component test execution, accessibility checks, and component-level visual regression.

## ADDED Requirements

### Requirement: Presentational components have isolated stories
Every presentational custom element under `src/components/` — a component whose rendered output is determined by its `@bindable` inputs rather than by RPC calls, routing, or authentication state — SHALL have at least one story that renders it in isolation without a running backend or an authenticated session. Route/page components and components that require live RPC, canvas physics, or auth context are OUT of scope and SHALL NOT be storied.

#### Scenario: Presentational component renders in isolation
- **WHEN** a story for a presentational component is opened
- **THEN** the component SHALL render its default state without any backend, RPC mock, or authenticated session
- **AND** its `@bindable` inputs SHALL be adjustable as controls that update the rendered component in place

#### Scenario: Distinct states are enumerated as stories
- **WHEN** a component has visually distinct states (e.g. loading, empty, error, variant, size)
- **THEN** each meaningful state SHALL be reachable as a named story via its inputs

#### Scenario: Route components are excluded
- **WHEN** the story set is reviewed
- **THEN** no story SHALL target a route/page component
- **AND** the previously existing route-targeted story SHALL have been removed

### Requirement: Component stories run as tests in CI
Stories SHALL be executed as automated component tests in a real browser during continuous integration. A story that fails to render, or whose interaction assertions fail, SHALL fail the build and block merge.

#### Scenario: Story render smoke test
- **WHEN** the CI component-test run executes a story
- **THEN** a story that renders without throwing SHALL pass
- **AND** a story that throws during render SHALL fail with the offending component identified

#### Scenario: Interaction assertions are verified
- **WHEN** a story defines an interaction sequence (e.g. clicking a control and asserting the result)
- **THEN** the CI run SHALL execute that sequence and fail if any assertion is not met

#### Scenario: CI gate blocks on component-test failure
- **WHEN** any component test fails
- **THEN** the overall CI success gate SHALL report failure and prevent merge

#### Scenario: Component tests are skipped when no relevant files change
- **WHEN** a pull request changes no story, component, or test-configuration files
- **THEN** the component-test job MAY be skipped without failing the CI success gate

### Requirement: Accessibility checks run on component stories
Automated accessibility checks SHALL run against component stories in CI, covering at least color contrast, ARIA attribute validity, and keyboard-reachability heuristics. Detected violations SHALL be reported and SHALL fail the component-test run.

#### Scenario: Accessible component passes checks
- **WHEN** a story renders a component with no detectable accessibility violations
- **THEN** the accessibility check for that story SHALL pass

#### Scenario: Accessibility violation fails the run
- **WHEN** a story renders a component with a detectable violation (e.g. insufficient contrast or an invalid ARIA attribute)
- **THEN** the accessibility check SHALL fail and identify the rule and component

### Requirement: Component-level visual regression detects unintended changes
Visual regression SHALL be performed at the component/story level by comparing rendered screenshots against committed baselines, using an in-repository comparator with no dependency on a paid external service. It SHALL be scoped to design-system components. An unintended visual change SHALL fail CI; an intended change SHALL be adoptable by updating the baseline.

#### Scenario: Unchanged component matches baseline
- **WHEN** a design-system component story is captured and compared to its baseline
- **THEN** a visually identical render SHALL pass within the configured pixel tolerance

#### Scenario: Visual drift fails the run
- **WHEN** a component's rendered output differs from its baseline beyond tolerance
- **THEN** the visual check SHALL fail and a diff artifact SHALL be made available for review

#### Scenario: First run establishes baselines
- **WHEN** no baseline exists for a story
- **THEN** the run SHALL generate and persist an initial baseline rather than fail

### Requirement: A single visual-regression pipeline is maintained
The frontend SHALL maintain exactly one visual-regression pipeline. Once component-level visual regression reaches parity with the pre-existing page-level (Playwright `mobile-visual`) pipeline, the page-level pipeline SHALL be retired so that visual coverage is not double-maintained.

#### Scenario: No duplicate visual pipelines after migration
- **WHEN** component-level visual regression is in place and at parity
- **THEN** the page-level `mobile-visual` project and its baselines SHALL be removed from CI and the repository

### Requirement: Unit and component test suites are isolated but jointly gated
The existing unit test suite and the browser-mode component/story test suite SHALL run as separate, independently runnable projects. Both SHALL be required to pass in CI. The existing unit-suite coverage thresholds SHALL be preserved after the test-runner upgrade.

#### Scenario: Suites run independently
- **WHEN** a developer runs the unit project or the component (browser) project by name
- **THEN** each SHALL run in isolation without requiring the other

#### Scenario: Both suites gate CI
- **WHEN** either the unit suite or the component suite fails
- **THEN** the CI success gate SHALL report failure

#### Scenario: Unit coverage thresholds are preserved
- **WHEN** the unit suite runs after the test-runner upgrade
- **THEN** coverage SHALL continue to be enforced with statements/functions/lines thresholds unchanged
- **AND** the branch threshold MAY be recalibrated to the new runner's branch-counting basis where the runner changes how branches are measured (Vitest 4 AST-aware remapping), so long as enforcement is not removed (see design D8)
