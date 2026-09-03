## 1. Toolchain upgrade & Storybook config minimization

- [ ] 1.1 Bump `aurelia`, `@aurelia/router`, `@aurelia/i18n`, `@aurelia/vite-plugin` to `2.0.0-rc.2`; run the full existing unit + smoke + e2e suites as the safety net (Risk R5)
- [ ] 1.2 Upgrade `@aurelia/storybook` `2.2.1 → 3.0.0` and `storybook` + `@storybook/builder-vite` `10.1 → 10.6`
- [ ] 1.3 Remove the hand-written `viteFinal` (`@aurelia/runtime-html` optimizeDeps exclusion) from `.storybook/main.ts`; delete `.storybook/preview.ts`; drop `@storybook/addon-links` if unused (D5)
- [ ] 1.4 Delete `src/routes/welcome/welcome-route.stories.ts` (route out of scope; spec: "Route components are excluded")
- [ ] 1.5 Verify `npm run storybook` (storybook dev) boots with no component stories yet

## 2. Vitest 4 migration & projects topology

- [ ] 2.1 Upgrade `vitest` and `@vitest/coverage-v8` `2.1.8 → 4.x`; review Vitest 4 breaking changes against the current unit suite (Risk R1)
- [ ] 2.2 Restructure `vitest.config.ts` into `test.projects` with a `unit` project carrying the current jsdom config verbatim (forks `--no-experimental-webstorage`, excludes `e2e/**`/`scripts/**`, v8 coverage thresholds statements/functions/lines 70 & branches 78)
- [ ] 2.3 Resolve OQ1: fold `vitest.scripts.config.ts` into the projects layout as a third project, or keep it standalone — decide by whether the Node-API script tests compose cleanly
- [ ] 2.4 Run `make test`; confirm the `unit` project is green and coverage is enforced at the preserved thresholds (spec: "Unit coverage thresholds are preserved")

## 3. Component-test project & PoC gate

- [ ] 3.1 Add dev deps: `@storybook/addon-vitest`, `@vitest/browser`, `@vitest/browser-playwright`, `@storybook/addon-a11y`
- [ ] 3.2 Add the `storybook` project to `vitest.config.ts`: `storybookTest({ configDir: '.storybook' })`, `browser: { enabled, headless, provider: playwright({}), instances: [{ browser: 'chromium' }] }`, `setupFiles: ['./.storybook/vitest.setup.ts']`; create `.storybook/vitest.setup.ts`
- [ ] 3.3 Verify the `storybook` project does NOT pull the app `vite.config.ts` build-only concerns (multi-entry `input`, VitePWA) into the browser build (Risk R2 / D6)
- [ ] 3.4 Register `addon-a11y` so accessibility checks run inside the browser project and fail on violations (spec: "Accessibility checks run on component stories" / D3)
- [ ] 3.5 PoC: author one story (e.g. `error-banner`) and run it via `vitest --project=storybook`; confirm `@storybook/addon-vitest` executes an Aurelia v3 story in browser mode. If it fails, fall back to `composeStories` portable stories (Risk R3 gate — do not fan out until green)
- [ ] 3.6 Add `test-storybook` script (`vitest --project=storybook`) to `package.json`

## 4. Author component stories

- [ ] 4.1 Write CSF3 stories colocated under `src/components/<name>/` for the presentational set: `loading-spinner`, `toast`, `snack-bar`, `error-banner`, `inline-error`, `state-placeholder`, `page-header`, `coach-mark`, `svg-icon`, `bottom-sheet` (D2)
- [ ] 4.2 For each, expose `@bindable` inputs as controls and enumerate visually distinct states as named stories (spec: "Distinct states are enumerated as stories")
- [ ] 4.3 Add `play` functions with interaction assertions where components have behavior (e.g. bottom-sheet open/close, toast dismiss) (spec: "Interaction assertions are verified")
- [ ] 4.4 Tag stories with `test` (and `autodocs`) so they execute under Vitest and generate docs
- [ ] 4.5 Confirm route/canvas/RPC/auth-bound components remain unstoried (spec: "Route components are excluded")

## 5. Component-level visual regression (Vitest toMatchScreenshot)

- [ ] 5.1 Add `toMatchScreenshot()` assertions for the design-system subset within the `storybook` browser project; set an initial pixel tolerance (OQ2)
- [ ] 5.2 Establish committed/artifact baselines with a first-run generation path (spec: "First run establishes baselines")
- [ ] 5.3 Confirm an intentional visual change is adoptable by updating the baseline and an unintended one fails with a diff artifact (spec: "Visual drift fails the run")

## 6. CI integration

- [ ] 6.1 Add a `storybook-test` job to `.github/workflows/ci.yaml` reusing the cached Playwright Chromium (`playwright-chromium-*` key); run `vitest --project=storybook`
- [ ] 6.2 Wire the visual baseline download/upload + diff-on-failure artifact steps for the component visual run (mirror the existing `visual` job pattern)
- [ ] 6.3 Extend `changes` `paths-filter` with `.storybook/**`, `**/*.stories.*`; add `storybook-test` (+ `storybook-test-skip`) to the `ci-success` `needs`/`allowed-skips` (spec: "Component tests are skipped when no relevant files change" / "CI gate blocks on component-test failure")
- [ ] 6.4 Verify a deliberately failing story (render, interaction, a11y, or visual) turns the `ci-success` gate red

## 7. Retire the duplicate visual pipeline

- [ ] 7.1 Confirm component-level visual regression is at parity for the design-system components (Risk R6 accepted: page-level route composition remains covered by e2e/smoke, not visual)
- [ ] 7.2 Remove the Playwright `visual` job (`mobile-visual` project) from `ci.yaml`, its `ci-success` wiring, and `e2e/__screenshots__/` baselines (spec: "A single visual-regression pipeline is maintained")

## 8. Documentation

- [ ] 8.1 Update `frontend/AGENTS.md` (Stories/Testing sections) with the story-authoring scope, `test-storybook` command, and the projects layout
