## Why

The frontend has shipped with Storybook since project init, but it is effectively dormant — one story (for a route) in seven months, and zero stories for the 27 components under `src/components/`. Presentational UI components have no isolated development surface, no per-state catalog, no automated accessibility checks, and no component-level visual regression. Meanwhile Storybook `@aurelia/storybook` 3.0 removes the framework boilerplate and Vitest 4 makes it possible to run stories as browser-mode component tests (and take component screenshots) using the Playwright Chromium the CI already installs. This is the moment to convert dead configuration into a maintained, CI-enforced component testing surface.

## What Changes

- **Upgrade the toolchain to latest**: `aurelia` (+ `@aurelia/router`, `@aurelia/i18n`, `@aurelia/vite-plugin`) to the latest RC, `@aurelia/storybook` `2.2.1 → 3.0.0`, `storybook` `10.1 → 10.6`.
- **BREAKING (dev tooling): upgrade Vitest `2.1.8 → 4.x`** (with `@vitest/coverage-v8`). Restructure `vitest.config.ts` into Vitest 4 `test.projects`: a `unit` project (jsdom, carrying the current unit suite + coverage thresholds) and a `storybook` project (browser mode via `@vitest/browser-playwright`, Chromium). Reconcile `vitest.scripts.config.ts` with the new projects layout.
- **Simplify Storybook config**: remove the hand-written `viteFinal` (`@aurelia/runtime-html` `optimizeDeps` exclusion) and the `.storybook/preview.ts` re-export — the v3 preset handles both.
- **Author component stories**: add CSF3 stories for the presentational components under `src/components/` (e.g. `loading-spinner`, `toast`, `snack-bar`, `error-banner`, `inline-error`, `state-placeholder`, `page-header`, `coach-mark`, `svg-icon`, `bottom-sheet`), with `@bindable`-driven controls, `play` functions for interaction assertions, and the `test` tag so stories run under Vitest.
- **Add accessibility testing**: introduce `@storybook/addon-a11y` and enforce a11y checks as part of the CI component-test run.
- **Migrate visual regression to Vitest**: replace the existing Playwright `mobile-visual` page-level visual regression with Vitest 4 browser-mode `toMatchScreenshot()` at the component/story level (pixelmatch/PNG, no paid SaaS), scoped to design-system components, reusing the existing baseline-as-artifact CI pattern. Retire the Playwright `mobile-visual` project once parity is met, to avoid double-maintaining two visual pipelines.
- **Wire CI**: add a `storybook-test` job to `.github/workflows/ci.yaml` (reusing the cached Playwright Chromium), extend `paths-filter` for `.storybook/**` and `*.stories.*`, and add it to the `ci-success` gate.
- **Remove the mis-targeted story**: delete `src/routes/welcome/welcome-route.stories.ts` — routes are the RPC/auth/routing integration layer and are out of scope for Storybook.

## Capabilities

### New Capabilities
- `storybook-component-testing`: Storybook-based isolated component development and CI-enforced component testing for the Aurelia 2 frontend — story authoring scope, browser-mode test execution, accessibility checks, component-level visual regression, and CI integration.

### Modified Capabilities
<!-- No existing capability's requirements change. Visual-regression behavior migrates into the new capability above; the retirement of the Playwright mobile-visual project is captured there and in tasks. -->

## Impact

- **Dependencies**: `aurelia*` RC bump; `@aurelia/storybook` 3; `storybook` 10.6; Vitest 2 → 4 + `@vitest/coverage-v8`; new `@storybook/addon-vitest`, `@vitest/browser`, `@vitest/browser-playwright`, `@storybook/addon-a11y`; remove `@storybook/addon-links` (optional).
- **Config**: `vitest.config.ts` (projects restructure), `vitest.scripts.config.ts`, `.storybook/main.ts`, `.storybook/preview.ts` (removed), new `.storybook/vitest.setup.ts`.
- **CI**: `.github/workflows/ci.yaml` — new `storybook-test` job, `paths-filter` and `ci-success` updates, retire the `visual` (Playwright `mobile-visual`) job after parity.
- **Tests/source**: new `*.stories.ts` beside components under `src/components/`; removal of `src/routes/welcome/welcome-route.stories.ts` and (after migration) `e2e/` mobile-visual specs + `e2e/__screenshots__/` baselines.
- **Risks to validate during apply**: Vitest 2→4 breaking changes against the existing unit suite/coverage; leakage of the app `vite.config.ts` (multi-entry input, VitePWA) into the Storybook browser project; and a PoC confirming `@storybook/addon-vitest` runs an Aurelia v3 story in browser mode before fanning out.
