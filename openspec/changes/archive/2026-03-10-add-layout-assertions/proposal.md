## Why

CSS layout bugs (like the 7-layer `height: 100%` relay chain failure in `simplify-shell-layout`) pass through all 300+ unit tests undetected because the current test suite has zero coverage of DOM geometry and CSS layout behavior. Layout regressions are only caught manually via browser inspection. Playwright Layout Assertions provide fast, deterministic, CI-friendly verification of structural layout invariants.

## What Changes

- Add Playwright-based layout assertion tests that verify bounding boxes, overflow behavior, and element sizing for critical routes.
- Add a mobile viewport project to the Playwright config for layout testing at the primary target device size (390×844).
- Add RPC route mocking to isolate layout tests from backend dependencies.
- Integrate layout tests into the existing `make check` pipeline.

## Capabilities

### New Capabilities
- `layout-assertions`: Playwright E2E tests that verify CSS layout invariants (element sizing, positioning, overflow, and containment) for the app shell and route components.

### Modified Capabilities
- `frontend-testing`: Add layout assertion tests as a new category alongside existing unit tests and PWA E2E tests.

## Impact

- **frontend/e2e/**: New test files for layout assertions.
- **frontend/playwright.config.mjs**: New mobile viewport project, RPC mock setup.
- **frontend/Makefile**: Integration of layout tests into `make check` pipeline.
- No changes to application code — tests only.
