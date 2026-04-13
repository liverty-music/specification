## ADDED Requirements

### Requirement: E2E selectors use data-testid for stability
All E2E test selectors for elements that are subject to refactoring SHALL use `data-testid` attributes instead of CSS class selectors, per [Playwright locator best practices](https://playwright.dev/docs/locators#locate-by-test-id).

#### Scenario: Concert highway scroll container uses data-testid
- **WHEN** an E2E test targets the concert scroll container
- **THEN** it SHALL use `page.getByTestId('concert-scroll')` instead of `page.locator('.concert-scroll')`

#### Scenario: Journey badge uses data-testid
- **WHEN** an E2E test targets a ticket journey badge on an event card
- **THEN** it SHALL use `page.getByTestId('journey-badge')` instead of `page.locator('.journey-badge')`

#### Scenario: Detail sheet journey section uses data-testid
- **WHEN** an E2E test targets the journey section in the event detail sheet
- **THEN** it SHALL use `page.getByTestId('sheet-journey')` instead of `page.locator('.sheet-journey')`

#### Scenario: Journey status buttons use data-testid with status qualifier
- **WHEN** an E2E test targets a specific journey status button
- **THEN** it SHALL use `[data-testid="journey-btn"][data-journey-status="tracking"]` (static testid combined with existing status attribute) instead of `.journey-btn[data-journey-status="tracking"]`
- **AND** the template SHALL use static `data-testid="journey-btn"` (not dynamic interpolation, per `lint-no-data-interpolation` rule)

#### Scenario: Dashboard loading indicator uses data-testid
- **WHEN** an E2E test targets the dashboard loading text
- **THEN** it SHALL use `page.getByTestId('dashboard-loading')` instead of `page.locator('.loading-text')`

#### Scenario: Welcome preview section uses data-testid
- **WHEN** an E2E test targets the welcome page preview section
- **THEN** it SHALL use `page.getByTestId('welcome-preview')` instead of `page.locator('.welcome-preview')`

#### Scenario: data-testid attributes are present in component templates
- **WHEN** a component template contains an element targeted by E2E tests
- **THEN** the element SHALL have a `data-testid` attribute with a kebab-case value matching its semantic purpose

### Requirement: E2E tests use Playwright native locator API without JS dispatch workarounds
E2E tests SHALL use Playwright's native locator API (`click()`, `fill()`, `check()`) instead of `page.evaluate()` for user interactions, per [Playwright actionability docs](https://playwright.dev/docs/actionability).

#### Scenario: Popover elements are dismissed before serial test interactions
- **WHEN** a serial-mode E2E test begins a new interaction after a prior test opened a popover
- **THEN** the test setup SHALL close any open popovers via `hidePopover()` before performing actions
- **AND** subsequent Playwright `click()` calls SHALL succeed without JS dispatch

#### Scenario: Visually-hidden radio inputs are clickable via labels
- **WHEN** an E2E test needs to select a radio option with a visually-hidden input whose label has readable text and does not use an event-sensitive binding (e.g. Aurelia `change.trigger`)
- **THEN** it SHALL use `page.getByLabel('label text').click()` per [Playwright getByLabel docs](https://playwright.dev/docs/locators#locate-by-label)
- **AND** it SHALL NOT use `page.evaluate()` to dispatch synthetic events
- **WHEN** the input has no readable label text or requires a native `change` event (e.g. Aurelia `change.trigger` binding)
- **THEN** it SHALL use `page.evaluate(() => el.dispatchEvent(new Event('change', { bubbles: true })))` — this is correct behavior, not a workaround (see Design Decision 4)

#### Scenario: Event card clicks use native Playwright click
- **WHEN** an E2E test clicks an event card to open the detail sheet and popovers have been cleaned up
- **THEN** it SHALL use `page.locator('[data-live-card]').first().click()` or equivalent Playwright locator
- **AND** it SHALL NOT use `page.evaluate(() => el.click())`

#### Scenario: Journey button clicks use native Playwright click
- **WHEN** an E2E test clicks a journey status button inside the detail sheet
- **THEN** it SHALL use `page.locator('[data-testid="journey-btn"][data-journey-status="tracking"]').click()` or equivalent
- **AND** it SHALL NOT use `page.evaluate(() => btn.click())`
