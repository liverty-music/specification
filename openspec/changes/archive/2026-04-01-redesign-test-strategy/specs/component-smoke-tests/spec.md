## MODIFIED Requirements

### Requirement: E2E console error smoke test
The test suite SHALL navigate to each public route in a real browser and verify that no console errors are emitted during page load. The test SHALL use `waitForLoadState('networkidle')` instead of `waitForTimeout()` for page settle detection.

#### Scenario: Public route loads without console errors
- **WHEN** Playwright navigates to a public route (e.g., `/`, `/welcome`, `/about`, `/discover`)
- **THEN** the page SHALL load successfully
- **AND** no `console.error` messages SHALL be emitted
- **AND** the test SHALL fail if any console error is detected

#### Scenario: Page settle uses networkidle instead of timeout
- **WHEN** the smoke test waits for the page to settle after navigation
- **THEN** it SHALL use `page.waitForLoadState('networkidle')` instead of `waitForTimeout()`

#### Scenario: Network errors are excluded from assertion
- **WHEN** a console error is caused by a failed network request (e.g., backend unavailable)
- **THEN** the test SHALL exclude network-related errors from the assertion
- **AND** only application-level errors (template compilation, JS exceptions) SHALL cause test failure

#### Scenario: CI runs smoke tests in parallel with lint and unit tests
- **WHEN** a pull request is opened or updated with frontend source changes
- **THEN** CI SHALL execute the Playwright `smoke` project as a job that runs in parallel with `lint`, `test`, and `security` jobs
- **AND** the `ci-success` gate SHALL require the `smoke` job to pass

#### Scenario: CI installs only required browser
- **WHEN** the `smoke` CI job installs Playwright browsers
- **THEN** it SHALL install only Chromium (not Firefox or WebKit)
- **AND** include OS-level dependencies via `--with-deps`
