## ADDED Requirements

### Requirement: 5-layer test architecture
The frontend test suite SHALL be organized into five distinct layers with clear boundaries, allowed tools, and assertion patterns per layer.

#### Scenario: Layer 1 — Unit Tests
- **WHEN** a test verifies a pure function, entity, or adapter
- **THEN** it SHALL use Vitest only (no `@aurelia/testing`, no Playwright)
- **AND** it SHALL reside in `src/**/*.spec.ts` alongside the source file

#### Scenario: Layer 2 — Component Integration Tests
- **WHEN** a test verifies component DOM output, DI wiring, bindable behavior, or template rendering
- **THEN** it SHALL use Vitest + `@aurelia/testing` `createFixture`
- **AND** it SHALL reside in `src/components/**/*.spec.ts` or `src/routes/**/*.spec.ts`
- **AND** it SHALL NOT require a running browser or Playwright

#### Scenario: Layer 3 — E2E Functional Tests
- **WHEN** a test verifies a user journey, page navigation, or error recovery flow
- **THEN** it SHALL use Playwright with `toBeVisible()`, `toHaveText()`, `toHaveURL()`, `toHaveCount()` assertions
- **AND** it SHALL reside in `e2e/functional/**/*.spec.ts`
- **AND** it SHALL NOT use `boundingBox()` or coordinate-based assertions

#### Scenario: Layer 4 — Visual Regression Tests
- **WHEN** a test verifies layout correctness, spatial positioning, or visual appearance
- **THEN** it SHALL use Playwright with `toHaveScreenshot()` assertions exclusively
- **AND** it SHALL reside in `e2e/visual/**/*.visual.spec.ts`
- **AND** baseline images SHALL be stored as CI artifacts, not committed to git

#### Scenario: Layer 5 — PWA / Infrastructure Tests
- **WHEN** a test verifies Service Worker registration, offline behavior, or install prompts
- **THEN** it SHALL use Playwright and MAY use `waitForFunction()` for inherently async SW operations
- **AND** it SHALL reside in `e2e/pwa/**/*.spec.ts`

### Requirement: Prohibited patterns per layer
Each test layer SHALL enforce specific prohibition rules to prevent test fragility.

#### Scenario: boundingBox() prohibited in Layers 3, 4, and 5
- **WHEN** a test in `e2e/functional/`, `e2e/visual/`, or `e2e/pwa/` calls `boundingBox()`
- **THEN** the test SHALL be considered a violation of the test strategy
- **EXCEPT** `boundingBox()` used solely to verify element existence or non-zero dimensions — without numeric coordinate comparisons — is permitted in Layer 3

#### Scenario: waitForTimeout() prohibited in Layers 1-4
- **WHEN** a test in Layer 1, 2, 3, or 4 calls `waitForTimeout()`
- **THEN** the test SHALL be considered a violation of the test strategy
- **AND** the wait SHALL be replaced with a web-first assertion or event-based wait

#### Scenario: coordinate assertions prohibited in Layers 1-3
- **WHEN** a test in Layer 1, 2, or 3 asserts on pixel coordinates, bounding box dimensions, or spatial relationships between elements
- **THEN** the test SHALL be considered a violation of the test strategy

### Requirement: CI pipeline maps layers to jobs
The CI workflow SHALL map each test layer to a dedicated job with appropriate configuration.

#### Scenario: Layer 2 runs in Test job
- **WHEN** CI executes the Test job
- **THEN** it SHALL run `make test` which includes both Layer 1 and Layer 2 tests via Vitest

#### Scenario: Layer 3 runs in E2E job
- **WHEN** CI executes the E2E job
- **THEN** it SHALL run Playwright projects `functional` and `pwa`

#### Scenario: Layer 4 runs in Visual Regression job
- **WHEN** CI executes the Visual Regression job
- **THEN** it SHALL download baseline screenshots from the main branch artifact
- **AND** it SHALL run Playwright project `mobile-visual`
- **AND** it SHALL upload diff images as artifacts on failure

#### Scenario: Baseline update on main merge
- **WHEN** a commit is merged to the main branch
- **THEN** CI SHALL run `npx playwright test --project=mobile-visual --update-snapshots`
- **AND** it SHALL upload the updated screenshots as a named artifact (`visual-baselines`)

### Requirement: E2E directory structure
The `e2e/` directory SHALL be organized by test layer purpose.

#### Scenario: Directory layout
- **WHEN** the test suite is inspected
- **THEN** the directory structure SHALL be:
  - `e2e/functional/` — Layer 3 E2E functional tests
  - `e2e/visual/` — Layer 4 visual regression tests
  - `e2e/pwa/` — Layer 5 PWA tests
  - `e2e/smoke/` — Console error smoke tests
