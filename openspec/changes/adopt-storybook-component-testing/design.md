## Context

See `proposal.md` — Why. Current relevant state (verified in-repo):

- `frontend/` is Aurelia 2 + Vite + CUBE CSS PWA. Storybook has been installed since project init but has one route-targeted story and zero component stories.
- `package.json` (dev): `@aurelia/storybook ^2.2.1`, `storybook ^10.1.11`, `@storybook/builder-vite ^10.1.11`, `vitest ^2.1.8`, `@vitest/coverage-v8 ^2.1.8`, `@playwright/test ^1.49.1`. App deps on `aurelia ^2.0.0-rc.1`.
- `.storybook/main.ts` carries a hand-written `viteFinal` that excludes `@aurelia/runtime-html` from `optimizeDeps`; `.storybook/preview.ts` re-exports `render`/`renderToCanvas`.
- `vitest.config.ts` = jsdom + `forks` pool with `--no-experimental-webstorage` (Node 25 localStorage workaround) + v8 coverage thresholds (statements/functions/lines 70, branches 78) + excludes `e2e/**`, `scripts/**`. `vitest.scripts.config.ts` is a separate config for Node-API script tests.
- `vite.config.ts` is heavy: three HTML entries (`index`/`admin`/`organizer`) via `rollupOptions.input`, `nodePolyfills`, `VitePWA` (injectManifest), a `plain-date-engine` alias.
- `.github/workflows/ci.yaml` runs `changes` (paths-filter) → `lint`/`test`/`security`/`smoke`/`e2e`/`visual` → `ci-success` (`alls-green`). A `visual` job already does self-hosted page-level visual regression: Playwright `--project=mobile-visual` with baselines stored as a GitHub artifact (`e2e/__screenshots__/`, `dawidd6/action-download-artifact`, 90-day retention). CI installs cached Playwright Chromium.

Verified upstream version facts (npm, Sept 2026): `aurelia` latest = `2.0.0-rc.2`; `@aurelia/storybook@3.0.0` peers `storybook ^10.5.6` + `aurelia ^2.0.0-rc.2`; `storybook` latest = `10.6.0`; `@storybook/addon-vitest` peers `vitest ^3||^4`, `storybook ^10.6.0`, `@vitest/browser ^3||^4`, `@vitest/browser-playwright ^4`; Vitest 4 ships browser-mode `toMatchScreenshot()` (pixelmatch/PNG).

## Goals / Non-Goals

**Goals:**
- One Vitest configuration that runs the existing unit suite (jsdom) and the new story-as-test suite (browser mode) as separate projects, jointly gated in CI.
- Component stories that double as render/interaction/a11y tests, plus component-level visual regression, with no paid SaaS.
- Convert dormant Storybook config into a maintained surface with the minimum boilerplate the v3 preset allows.

**Non-Goals:**
- Storying route/page components, canvas (`dna-orb`), or RPC/auth-bound components (design decision D2).
- Replacing the existing `@aurelia/testing` `createFixture` integration/smoke tests (they stay; this is additive at the component-visual/interaction layer).
- Broad visual regression across all components — visual coverage is limited to design-system components (spec: "component-level visual regression").

## Decisions

### D1. Test-runner topology: Vitest 4 `test.projects` (not workspaces, not separate CLI configs)
Storybook's official guidance is: existing Vitest tests + addon → use **test projects** on Vitest ≥4, workspace on 3.x. We upgrade to Vitest 4, so a single `vitest.config.ts` with `test.projects: [unit, storybook]` is the target. The `unit` project carries the current jsdom config verbatim (pool `execArgv`, coverage thresholds, excludes). The `storybook` project uses `storybookTest({ configDir: '.storybook' })` + `browser: { enabled, headless, provider: playwright({}), instances: [{ browser: 'chromium' }] }` + `setupFiles: ['./.storybook/vitest.setup.ts']`.
- *Alternatives:* Vitest 3 + `vitest.workspace.ts` (rejected — user approved latest; projects is the forward path and avoids a soon-legacy workspace file). Keeping a third separate CLI config like today's `vitest.scripts.config.ts` for storybook (rejected — the addon is designed around projects/workspace; separate configs lose unified `vitest` runs and coverage merge).
- *`vitest.scripts.config.ts`:* fold in as a third project only if it composes cleanly; otherwise leave as a standalone config invoked by its existing script. Decide during apply (Open Question OQ1).

### D2. Story scope: presentational components only, colocated
Story files live beside components (`src/components/<name>/<name>.stories.ts`), matching `.storybook/main.ts` `stories` glob. We story the input-driven primitives (`loading-spinner`, `toast`, `snack-bar`, `error-banner`, `inline-error`, `state-placeholder`, `page-header`, `coach-mark`, `svg-icon`, `bottom-sheet`, and similar). We explicitly exclude route components, `dna-orb` (canvas/Matter.js), and anything requiring live RPC/auth — the current `welcome-route` story proves routes only render a degraded fallback without a backend. This mirrors the existing `component-smoke-tests` exclusion of `dna-orb`.
- *Rationale:* Storybook's value and the browser-mode test signal are highest where output is a pure function of `@bindable` inputs; forcing stateful components in needs heavy mocking and yields brittle tests.

### D3. a11y via `@storybook/addon-a11y`, enforced in test
Add `@storybook/addon-a11y`; configure it to run within the Vitest browser project so violations fail the run (not just surface in the UI). `@aurelia/storybook` documents addon-a11y support.

### D4. Visual regression via Vitest 4 `toMatchScreenshot`, committed baselines
Use Vitest 4 browser-mode `toMatchScreenshot()` (pixelmatch/PNG, in-repo, free) for design-system components. Baselines are **committed to git** (next to the stories, the `toMatchScreenshot` default) rather than stored as a CI artifact: baseline changes are then reviewable in the PR diff and never expire. First-run generation creates them; an unintended diff fails CI and uploads a diff image as a failure artifact for inspection. Once at parity, retire the Playwright `mobile-visual` job and `e2e/__screenshots__/` baselines so only one visual pipeline is maintained (spec: "A single visual-regression pipeline is maintained").
- *Alternatives:* Chromatic (rejected — paid SaaS; repo already proves self-hosted works). Baseline-as-artifact like today's `mobile-visual` job (rejected — the 90-day artifact expiry and non-reviewable baseline updates are exactly why we move to committed baselines; tolerable for many page-level shots, not for the small design-system component set). Keep Playwright `mobile-visual` in parallel (rejected — double maintenance; user asked to switch if Vitest is maintainable). Storybook test-runner + jest-image-snapshot (rejected — older path, extra harness vs. the browser project we already stand up).

### D5. Storybook config minimization under v3
Remove the `viteFinal` `optimizeDeps` exclusion and `.storybook/preview.ts` re-export; the v3 preset handles Vite optimization and rendering. `main.ts` reduces to `stories`, `addons` (`addon-a11y`, `addon-vitest`; drop `addon-links` unless used), and `framework: '@aurelia/storybook'`.

### D6. Isolate the app Vite config from the Storybook browser project
The app `vite.config.ts` carries build-only concerns (three-entry `rollupOptions.input`, `VitePWA`) that must not leak into the Storybook browser test project. The `storybookTest` plugin composes Storybook's own Vite config from `configDir`; the project should rely on that rather than blindly `extends`-ing the full app config. Multi-entry `input` is build-only (ignored under test) and `VitePWA` already has `devOptions.enabled: false`, but this is a verified-during-apply item (Risk R2).

### D7. Sequencing: upgrade → migrate → PoC → fan out → CI → retire
Land the dependency upgrades and config simplification first (Storybook dev boots), then the Vitest 4 unit migration (green unit suite), then a single-component PoC proving `@storybook/addon-vitest` runs an Aurelia v3 story in browser mode, then fan out stories, then wire the CI job, then retire the Playwright visual pipeline. This front-loads the two riskiest unknowns (Vitest 4 breakage, addon×Aurelia) before broad authoring.

## Risks / Trade-offs

- **R1 — Vitest 2→4 is the real cost, not Storybook.** Two majors across the existing unit suite (config shape, coverage reporter, API deprecations). → Migrate and get the `unit` project green *before* adding the `storybook` project; treat coverage-threshold parity as an acceptance gate.
- **R2 — App Vite config leaking into the browser project** (VitePWA/service worker, multi-entry). → Rely on `storybookTest` `configDir` composition (D6); verify the storybook project builds without pulling PWA/entry config; scope `extends` narrowly if used.
- **R3 — `@storybook/addon-vitest` × Aurelia v3 unproven in this repo.** The addon works via portable stories, which `@aurelia/storybook` v3 supports, but browser-mode execution for Aurelia is not prominently documented. → Gate fan-out behind a one-component PoC (D7); if it fails, fall back to `composeStories` portable stories run directly in the browser project.
- **R4 — CI time/flake from a new browser job.** → Reuse the existing cached Chromium; run headless Chromium only; keep visual tolerance conservative; keep the job behind `paths-filter` so unrelated PRs skip it.
- **R5 — Aurelia rc.1→rc.2 app-wide bump** may carry RC breaking changes beyond Storybook. → Land it as the first step with the full existing test/e2e suite as the safety net; independent of the Storybook work if it must be split.
- **R6 — Losing page-level visual coverage when retiring `mobile-visual`.** Component-level screenshots don't cover full-page layout composition. → Only retire after confirming design-system component coverage is the intended replacement; accept the scope reduction explicitly (page-level regressions for route composition are covered by e2e/smoke, not visual).

## Migration Plan

1. Bump `aurelia*` to rc.2, `@aurelia/storybook` 3, `storybook` 10.6; remove `viteFinal`/`preview.ts`; delete `welcome-route.stories.ts`. Verify `storybook dev` boots.
2. Upgrade Vitest 2→4 + coverage-v8; restructure into `test.projects` with the `unit` project; `make test` green at existing thresholds.
3. Add `@storybook/addon-vitest` + `@vitest/browser(-playwright)` + `addon-a11y`; add the `storybook` project + `.storybook/vitest.setup.ts`; PoC one component in browser mode (R3 gate).
4. Author stories for the presentational set (controls + `play` + `a11y`); add `toMatchScreenshot` visual for design-system components.
5. Add the `storybook-test` CI job (cached Chromium; `paths-filter` for `.storybook/**`, `*.stories.*`; `ci-success` gate).
6. After parity, retire the Playwright `visual`/`mobile-visual` job and `e2e/__screenshots__/`.

**Rollback:** Each step is independently revertable; the dependency bump (step 1) and Vitest migration (step 2) are the only wide-blast-radius steps and are guarded by the full existing test/e2e suites. The Storybook project is additive — reverting it does not touch the unit suite.

## Open Questions

- **OQ1:** Fold `vitest.scripts.config.ts` into `test.projects` as a third project, or keep it standalone? Decide during step 2 based on whether the Node-API script tests compose cleanly under the projects layout (does not affect specs or the CI gate design).
- **OQ2:** Exact visual tolerance and which subset qualifies as "design-system components" for `toMatchScreenshot` — tune during step 4; does not change the approach.
