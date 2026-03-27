## Context

The frontend has 121 E2E tests across 17 spec files. 50 tests use `boundingBox()` for layout verification and 15 use `waitForTimeout()`. These patterns cause deterministic CI failures — coach mark tests failed on every run due to CSS Anchor Positioning inside popover top layers. The Aurelia 2 testing documentation recommends E2E tests verify user journeys via `toBeVisible`/`toHaveText`, not coordinates. Layout verification belongs in a separate Visual Regression layer.

Current test structure:
- `src/` — 10 unit/component spec files (Vitest + @aurelia/testing)
- `e2e/` — 17 Playwright spec files mixing functional, layout, visual, and PWA concerns
- `e2e/layout/` — 6 files with `assertions.ts` helper (all `boundingBox` based)

CI pipeline runs 4 Playwright projects: `chromium`, `onboarding`, `smoke`, `mobile-layout`.

## Goals / Non-Goals

**Goals:**
- Establish a 5-layer test strategy: Unit → Component Integration → E2E Functional → Visual Regression → PWA
- Eliminate all `boundingBox()` coordinate assertions from E2E tests
- Eliminate all `waitForTimeout()` from non-PWA tests
- Move DOM structure/text verification from E2E to Component Integration (Vitest)
- Add Visual Regression layer using `toHaveScreenshot()` with CI artifact-based baselines
- Create Component Integration tests for 6 untested components

**Non-Goals:**
- Third-party visual regression tools (Percy, Chromatic) — Playwright built-in is sufficient
- Cross-browser visual testing — single Chromium baseline for now
- Refactoring component source code — tests only

## Decisions

### Decision 1: 5-layer test architecture

```
Layer    Tool                         Scope                    Allowed Assertions
─────    ─────────────────────────    ─────────────────────    ──────────────────────
1 Unit   Vitest                       Pure functions, entities expect(), toBe()
2 Comp   Vitest + @aurelia/testing    Component DOM, DI, bind  textContent, querySelector
3 E2E    Playwright                   User journeys            toBeVisible, toHaveText, toHaveURL
4 Visual Playwright                   Layout, positioning      toHaveScreenshot() ONLY
5 PWA    Playwright                   SW, offline, install     waitForFunction (SW async is inherent)
```

**Why**: Aurelia 2 officially recommends Layers 1-3. Layer 4 fills the gap where layout tests were incorrectly placed in Layer 3. Layer 5 isolates PWA-specific async patterns that legitimately need `waitForFunction`.

**Alternative considered**: Keep layout tests in E2E with relaxed assertions (`toBeInViewport`). Rejected because it loses regression detection — `toBeInViewport` doesn't catch subtle layout shifts.

### Decision 2: Artifact-based screenshot baselines (not git)

Baseline screenshots are stored as CI artifacts on the main branch, not committed to git.

**CI flow:**
1. `main` branch: `npx playwright test --update-snapshots` → upload `__screenshots__/` as artifact
2. PR branches: download main's artifact → `npx playwright test` (compare) → upload diff on failure
3. Intentional visual changes: re-run with `--update-snapshots`, reviewer approves via diff artifact

**Why**: Avoids git history bloat. Screenshot baselines are binary files that change frequently (font rendering, Chromium version bumps). Git LFS is an alternative but adds complexity.

**Alternative considered**: Commit to repo (simple, always available). Rejected per user requirement — git history should not contain binary baselines.

### Decision 3: `git mv` for directory restructuring

```
e2e/layout/*.layout.spec.ts  → e2e/visual/*.visual.spec.ts
e2e/onboarding-flow.spec.ts  → e2e/functional/onboarding-flow.spec.ts
e2e/pwa-*.spec.ts            → e2e/pwa/pwa-*.spec.ts
```

**Why**: `git mv` preserves blame/log history. File content will be rewritten (layout → screenshot) but authorship tracking is maintained.

### Decision 4: Component Integration tests use `createFixture` pattern

New Layer 2 tests follow the Aurelia 2 `createFixture` pattern with DI mocks:

```typescript
const { appHost, startPromise, stop } = createFixture(
  '<bottom-sheet open.bind="true"><p>Content</p></bottom-sheet>',
  class App { },
  [BottomSheet],
  [Registration.instance(IAnimationService, mockAnimation)]
);
await startPromise;
// assert DOM structure
await stop(true);
```

**Why**: Runs in Node.js (no browser), ~100ms per test vs ~seconds for Playwright. Covers DOM structure, binding, lifecycle — the majority of what `layout/*.spec.ts` currently tests via slow `boundingBox` assertions.

### Decision 5: Playwright config project mapping

```
Project Name         testMatch                    Device        CI Job
─────────────────    ──────────────────────       ──────────    ────────
functional           e2e/functional/**            Desktop       E2E
onboarding           e2e/functional/onboarding-*  Pixel 7       Smoke
smoke                e2e/smoke/**                 Desktop       Smoke
mobile-visual        e2e/visual/**                iPhone 14     Visual
pwa                  e2e/pwa/**                   Desktop       E2E
```

### Decision 6: `waitForTimeout` replacement patterns

| Current Pattern | Replacement |
|---|---|
| `waitForTimeout(100)` after scroll | `page.evaluate(() => new Promise(r => el.addEventListener('scrollend', r, {once:true})))` |
| `waitForTimeout(2000-5000)` for animation | `expect(el).not.toBeVisible({ timeout: N })` |
| `waitForTimeout(100)` between actions | Remove (synchronous operations don't need delay) |
| `waitForTimeout(2000)` for console errors | `page.waitForLoadState('networkidle')` |
| `waitForTimeout(2000-5000)` in PWA tests | Keep `waitForFunction` (SW registration is inherently async) |

## Risks / Trade-offs

**[R1] Screenshot baselines diverge between CI runners** → Pin Playwright version in `package.json` (exact, not caret). Playwright bundles its own Chromium, so rendering is deterministic across Linux runners. If flaky, add `maxDiffPixelRatio: 0.01` threshold.

**[R2] Baseline management overhead** → First-time setup requires manual `--update-snapshots` run. Automate via CI: on main merge, always update and upload baselines. PRs only compare.

**[R3] Component Integration tests may not catch all visual regressions** → By design. Layer 2 catches DOM/binding bugs, Layer 4 catches visual regressions. Both are needed.

**[R4] Large scope (121 tests to reorganize)** → Execute as single batch. Partial migration creates confusing dual patterns.

**[R5] `page.evaluate()` JS dispatch workarounds remain in E2E** → These are necessary because `page-help` popover intercepts Playwright pointer events. Not an anti-pattern per se — it's a workaround for Aurelia's top-layer rendering in popover. Document as known pattern.
