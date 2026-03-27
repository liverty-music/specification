## Why

The `refine-frontend-testing` change (PR #360) addresses unit test layer improvements (createFixture adoption, infra bug fixes, test isolation) but leaves unresolved the **structural root causes** that caused cascading CI failures during the concert-highway CE extraction (PR #298). Specifically: dual jsdom management in `test/setup.ts` causing `document is not defined` errors, Aurelia template import chains triggering uncontrolled module graph expansion in vitest, fragile CSS-class-based E2E selectors breaking on refactors, and pervasive `page.evaluate()` JS dispatch workarounds bypassing Playwright's auto-wait. These issues will recur on every non-trivial component refactoring unless the test infrastructure itself is hardened.

## What Changes

- **Resolve dual jsdom management**: Eliminate the manual `new JSDOM()` + `Object.assign(globalThis, ...)` in `test/setup.ts` that conflicts with vitest's built-in `environment: 'jsdom'`. Align with vitest's environment lifecycle so teardown ordering is deterministic.
- **Contain Aurelia template module graph expansion**: Establish a strategy to prevent `<import from="...">` in `.html` templates from causing vitest to recursively load the entire component dependency tree. Introduce global CE registration guidelines and `vi.mock()` containment patterns.
- **Introduce data-testid E2E selector strategy**: Migrate critical E2E selectors from CSS classes (`.concert-scroll`, `.journey-badge`) to stable `data-testid` attributes on components, reducing selector breakage on refactors.
- **Eliminate page.evaluate() JS dispatch workarounds**: Fix the application-layer issues (page-help dismiss-zone interception, popover top-layer blocking, visually-hidden form controls) that force E2E tests to bypass Playwright's native locator API.
- **Add CE composition integration tests**: Create `createFixture`-based tests that mount parent+child CE combinations to catch layout propagation issues (display:inline default, grid/flex chain breaks) before E2E.
- **Add dashboard-route integration test**: Cover the most complex route component (3 service injections, 5 state flags, 6 child CEs) which currently has zero test coverage after the previous spec was deleted.
- **Evaluate vitest environment optimization**: Assess `happy-dom` vs `jsdom`, per-file environment annotations, and vitest `projects` feature to separate unit (node) from integration (dom) tests for faster CI.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `frontend-testing`: Resolve dual jsdom management, contain template module graph expansion, add CE composition tests, add dashboard-route tests, optimize vitest environment configuration
- `layout-assertions`: Introduce data-testid selector strategy, eliminate page.evaluate() JS dispatch workarounds in E2E tests

## Impact

- **frontend repo**: `test/setup.ts` (jsdom alignment), `vitest.config.ts` (environment optimization), `src/components/**/*.html` (data-testid attributes), `src/components/page-help/` (dismiss-zone pointer-events fix), `e2e/**/*.spec.ts` (selector migration, JS dispatch removal), new test files for CE composition and dashboard-route
- **No API or dependency changes**: All changes are internal to the frontend repo
- **No breaking changes**: Existing tests continue to work; changes are additive or fix silent bugs
- **CI**: Faster test execution from environment optimization; more stable E2E from selector hardening
