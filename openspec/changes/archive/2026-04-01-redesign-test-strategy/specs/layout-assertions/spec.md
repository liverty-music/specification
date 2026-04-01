## MODIFIED Requirements

### Requirement: Shell layout structural integrity
The visual regression suite SHALL verify that the app shell layout renders correctly at mobile viewport (390×844) using screenshot comparison.

#### Scenario: Shell layout matches baseline
- **WHEN** any public route is loaded at 390×844 viewport
- **THEN** the page screenshot SHALL match the baseline image within the configured pixel tolerance

#### Scenario: Shell layout after scroll matches baseline
- **WHEN** the content area is scrolled
- **THEN** the page screenshot SHALL match the post-scroll baseline (header fixed, nav pinned)

### Requirement: Discover page layout containment
The visual regression suite SHALL verify that the discover page layout renders correctly at mobile viewport using screenshot comparison.

#### Scenario: Discover layout matches baseline
- **WHEN** the discover page is loaded at 390×844 viewport in bubble mode
- **THEN** the page screenshot SHALL match the baseline image

#### Scenario: Discover search mode matches baseline
- **WHEN** the discover page is in search mode with results displayed
- **THEN** the page screenshot SHALL match the search mode baseline image

### Requirement: Visual regression uses toHaveScreenshot exclusively
The visual regression test layer SHALL use Playwright's `toHaveScreenshot()` as the sole assertion method, replacing all `boundingBox()` coordinate assertions.

#### Scenario: No boundingBox in visual tests
- **WHEN** the visual regression test files are inspected
- **THEN** zero calls to `boundingBox()` SHALL be present

#### Scenario: No coordinate calculations in visual tests
- **WHEN** the visual regression test files are inspected
- **THEN** zero coordinate arithmetic assertions (`.x`, `.y`, `.width`, `.height` comparisons) SHALL be present

#### Scenario: Screenshot configuration
- **WHEN** `toHaveScreenshot()` is called
- **THEN** it SHALL use `animations: 'disabled'` to eliminate transition flakiness
- **AND** it SHALL use a `maxDiffPixelRatio` threshold to absorb minor rendering differences

### Requirement: Layout tests independent of backend
The visual regression suite SHALL not depend on a running backend service.

#### Scenario: Tests pass without backend
- **WHEN** visual regression tests are run with no backend available
- **THEN** all tests SHALL pass using mocked RPC responses via `page.route()`

## REMOVED Requirements

### Requirement: Layout test execution performance
**Reason**: The 5-second budget was defined for `boundingBox()`-based tests. Visual regression tests using `toHaveScreenshot()` have different performance characteristics (screenshot capture overhead). A fixed time budget is replaced by CI job timeout.
**Migration**: CI job timeout (15 minutes) serves as the execution budget. No per-test time assertion needed.
