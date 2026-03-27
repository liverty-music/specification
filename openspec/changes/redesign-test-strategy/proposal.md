## Why

The frontend test suite has 50 tests using `boundingBox()` coordinate assertions and 15 tests using `waitForTimeout()` — both anti-patterns that cause flaky CI failures. Coach mark onboarding tests failed consistently on every CI run due to CSS Anchor Positioning layout timing. The root cause is a missing Visual Regression layer: layout verification is forced into E2E tests that aren't designed for spatial assertions. Additionally, many tests that could run locally as fast Component Integration tests (Vitest + `@aurelia/testing`) are only covered by slow Playwright E2E tests.

## What Changes

- Introduce a 5-layer test strategy aligned with Aurelia 2 official recommendations: Unit, Component Integration, E2E Functional, Visual Regression, PWA
- Replace all `boundingBox()` coordinate assertions in `e2e/layout/` with `toHaveScreenshot()` visual regression tests
- Move DOM structure and text verification tests from E2E to Component Integration layer (Vitest + `createFixture`)
- Eliminate all `waitForTimeout()` calls in non-PWA tests (replace with web-first assertions)
- Restructure `e2e/` directory: `functional/`, `visual/`, `pwa/`, `smoke/`
- Add CI workflow for visual regression with artifact-based baseline management (not committed to git)
- Create new Component Integration tests for untested components: `bottom-sheet`, `coach-mark`, `snack-bar`, `celebration-overlay`, `concert-highway`, `bottom-nav-bar`

## Capabilities

### New Capabilities
- `test-strategy`: Defines the 5-layer test architecture, layer boundaries, allowed assertion patterns per layer, and CI pipeline mapping

### Modified Capabilities
- `frontend-testing`: Update testing spec to reflect 5-layer strategy, add Visual Regression requirements, update Component Integration test coverage expectations
- `layout-assertions`: Replace coordinate-based assertions with `toHaveScreenshot()` visual regression, redefine what "layout correctness" means in the test suite
- `component-smoke-tests`: Expand scope to include Component Integration tests for coach-mark, bottom-sheet, celebration-overlay, snack-bar, concert-highway

## Impact

- **e2e/layout/**: All 6 spec files rewritten as visual regression tests, `assertions.ts` helper deleted
- **e2e/**: Directory restructured into `functional/`, `visual/`, `pwa/`, `smoke/`
- **src/components/**: ~6 new `.spec.ts` files for Component Integration tests
- **playwright.config.mjs**: Project names updated (`mobile-layout` → `mobile-visual`), snapshot config added
- **.github/workflows/ci.yaml**: New Visual Regression job with artifact-based baseline management
- **.gitignore**: Add `e2e/__screenshots__/` (baselines stored as CI artifacts)
- **Makefile**: Update `make test` and `make check` targets if needed
