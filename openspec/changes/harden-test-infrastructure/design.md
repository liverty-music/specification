## Context

During the concert-highway CE extraction (PR #298), five distinct CI failures cascaded from structural weaknesses in the test infrastructure:

1. **`document is not defined`** — vitest's jsdom teardown conflicted with a manually-created JSDOM instance in `test/setup.ts`, leaving stale `globalThis.document` references
2. **CE height: 0** — Custom Elements default to `display: inline`, breaking grid/flex height propagation. No integration test detected this before E2E.
3. **Selector breakage** — `.concert-scroll` moved inside a CE, breaking 4 E2E tests relying on that CSS class
4. **`promise.bind` comment nodes** — Aurelia's template directives inject comment nodes that break parent-child layout chains. No unit/integration test existed for this.
5. **`page.evaluate()` workarounds** — 13+ E2E test sites bypass Playwright's locator API via JS dispatch due to page-help overlay interception and popover top-layer blocking

The companion `refine-frontend-testing` change (PR #360) addresses unit test quality (createFixture adoption, infra bug fixes). This change targets the **structural causes** that make refactoring unsafe.

**Key documentation references:**

| Topic | Source |
|-------|--------|
| Vitest environment lifecycle | https://vitest.dev/guide/environment.html |
| Vitest per-file environments | https://vitest.dev/guide/environment.html#environments-for-specific-files |
| Vitest projects feature | https://vitest.dev/guide/#projects-support |
| Vitest mocking modules | https://vitest.dev/guide/mocking.html |
| Vitest common errors | https://vitest.dev/guide/common-errors.html |
| Aurelia createFixture | https://docs.aurelia.io/developer-guides/overview/testing-components |
| Aurelia fluent API | https://docs.aurelia.io/developer-guides/overview/fluent-api |
| Aurelia DI mocking | https://docs.aurelia.io/developer-guides/overview/mocks-spies |
| Playwright locators best practices | https://playwright.dev/docs/locators |
| Playwright test isolation | https://playwright.dev/docs/browser-contexts |

## Goals / Non-Goals

**Goals:**
- Eliminate dual jsdom management so vitest teardown is deterministic
- Contain Aurelia template `<import>` module graph expansion to prevent cascading `vi.mock()` requirements
- Introduce `data-testid` selector strategy for E2E resilience
- Remove `page.evaluate()` JS dispatch workarounds by fixing application-layer issues
- Add CE composition integration tests (parent + child CE layout verification)
- Add dashboard-route integration test (most complex, currently untested route)
- Evaluate and adopt vitest environment optimization (happy-dom, per-file env, projects)

**Non-Goals:**
- Rewriting existing passing tests (additive only)
- Changing component source code beyond what's needed for testability (data-testid attributes, pointer-events fixes)
- Achieving 100% E2E selector migration in one pass (incremental, critical paths first)
- Adding new E2E test scenarios (stabilize existing ones)

## Decisions

### Decision 1: Unify jsdom management — let vitest own the environment

**Choice:** Remove the manual `new JSDOM(...)` and `Object.assign(globalThis, ...)` from `test/setup.ts`. Let vitest's `environment: 'jsdom'` be the single source of truth. Keep only `BrowserPlatform` initialization and fixture cleanup hooks. Disable Node.js 25's built-in Web Storage via `--no-experimental-webstorage` so jsdom can provide its own working implementation.

**Rationale (per [Vitest Environment docs](https://vitest.dev/guide/environment.html)):**
Vitest manages environment lifecycle automatically — setup before tests, teardown after. Creating a second JSDOM instance causes:
- Two `window` objects (vitest's and the manual one)
- `globalThis.document` pointing to the manual JSDOM, but vitest tearing down its own
- After teardown, Aurelia module resolution still references the stale manual JSDOM globals

**Node.js 25+ localStorage conflict (discovered during implementation):**
Node.js 25 unflagged `--experimental-webstorage` ([nodejs/node#57666](https://github.com/nodejs/node/pull/57666)), providing `globalThis.localStorage` as an empty proxy object where `.getItem`, `.setItem`, `.clear()` are all `undefined`. jsdom detects this existing property and skips its own Web Storage polyfill. This is tracked in [vitest-dev/vitest#8757](https://github.com/vitest-dev/vitest/issues/8757), [happy-dom#1950](https://github.com/capricorn86/happy-dom/issues/1950), and [nodejs/node#60303](https://github.com/nodejs/node/issues/60303).

**Fix:** Add `--no-experimental-webstorage` to vitest's fork worker `execArgv`. This removes Node's broken localStorage entirely, letting jsdom provide its own working Web Storage implementation.

```typescript
// vitest.config.ts — disable Node.js 25+ built-in Web Storage
poolOptions: {
  forks: {
    execArgv: ['--no-experimental-webstorage'],
  },
},
```

```typescript
// BEFORE: test/setup.ts (PROBLEMATIC — dual jsdom)
import { JSDOM } from 'jsdom'
const jsdom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost',
})
const { window } = jsdom
Object.assign(globalThis, {
  window, document: window.document, navigator: window.navigator,
  Node: window.Node, HTMLElement: window.HTMLElement,
  localStorage: window.localStorage, // ...
})

// AFTER: test/setup.ts (vitest owns jsdom, Node.js webstorage disabled)
import { BrowserPlatform } from '@aurelia/platform-browser'
import { type IFixture, onFixtureCreated, setPlatform } from '@aurelia/testing'
import { beforeAll, afterEach } from 'vitest'

function bootstrapTestEnv() {
  const platform = new BrowserPlatform(window as unknown as Window & typeof globalThis)
  setPlatform(platform)
  BrowserPlatform.set(globalThis, platform)
}

const fixtures: IFixture<object>[] = []
beforeAll(() => {
  bootstrapTestEnv()
  onFixtureCreated((fixture) => fixtures.push(fixture))
})

afterEach(async () => {
  await Promise.all(
    fixtures.map((f) => {
      const result = f.stop?.(true) ?? (f as any).tearDown?.()
      return result?.catch?.(() => {}) ?? Promise.resolve()
    }),
  )
  fixtures.length = 0
})
```

**Verification:** After this change:
- `jsdom` SHALL NOT appear in `test/setup.ts` imports
- `--localstorage-file` warning SHALL NOT appear in test output
- `localStorage.clear()` SHALL work in all test files

**Alternative considered:** MemoryStorage polyfill in `test/setup.ts`.
**Why rejected:** Polyfill shadows jsdom's implementation, adding maintenance burden. The `--no-experimental-webstorage` flag is the vitest community's recommended workaround ([vitest#8757](https://github.com/vitest-dev/vitest/issues/8757)) and will be removable once Node.js stabilizes Web Storage behavior.

**Alternative considered:** Switch to `environment: 'node'` and keep manual JSDOM.
**Why rejected:** Per vitest docs, `jsdom` environment provides proper lifecycle management. Fighting the framework's environment system is the root cause of the timing bugs.

### Decision 2: Contain template module graph via global CE registration + import guards

**Choice:** Establish a convention that all shared CEs are registered globally in `main.ts` (already partially done) and templates use CE tag names directly without `<import from="...">`. For tests, import the CE class directly — never via a route module.

**Rationale (per [Vitest Mocking Modules](https://vitest.dev/guide/mocking.html#how-it-works)):**
Vitest transforms `import` statements and evaluates modules eagerly. Aurelia's convention-based `.ts` → `.html` auto-resolution means importing a route module triggers:

```
app-shell.ts
  └── @route({ component: import('./dashboard-route') })
       └── dashboard-route.ts → dashboard-route.html (convention)
            └── <import from="concert-highway">
                 └── concert-highway.ts → concert-highway.html
                      └── <import from="event-card">
                           └── event-card.ts → resolve(INode) → document 💥
```

**The containment strategy has three pillars:**

**Pillar A: Global CE registration (already in place)**
All shared CEs registered in `main.ts`. Templates use `<concert-highway>` without `<import>`.

**Pillar B: Test import isolation**
Tests import the target CE directly, not through parent routes:
```typescript
// GOOD: Direct import — no module chain
import { ConcertHighway } from '../../src/components/live-highway/concert-highway'

// BAD: Import via route — triggers entire template chain
import { DashboardRoute } from '../../src/routes/dashboard/dashboard-route'
```

**Pillar C: vi.mock() for HTML templates when route-level tests are needed**
For route-level tests that must import the route module, mock the HTML template to prevent Aurelia's convention from loading child templates:

```typescript
// Per Vitest docs: vi.mock() is hoisted to top of file
vi.mock('../../src/routes/dashboard/dashboard-route.html', () => ({
  default: '<div></div>'  // minimal template, no <import> chains
}))
```

**Alternative considered:** Use vitest `server.deps.inline` to control which modules are transformed.
**Why rejected:** `server.deps.inline` controls external dependency transformation, not internal module resolution. The chain expansion is within the project's own source files.

### Decision 3: Adopt data-testid attributes for E2E selector stability

**Choice:** Add `data-testid` attributes to all elements that are targeted by E2E tests. Migrate critical E2E selectors from CSS classes to `data-testid`.

**Rationale (per [Playwright Locators docs](https://playwright.dev/docs/locators#locate-by-test-id)):**
Playwright explicitly recommends `data-testid` for test stability:
> "Test IDs are the most resilient locator strategy. [...] Since test IDs are dedicated to testing, they won't break when you refactor CSS or change text content."

```html
<!-- BEFORE: CSS class selector (breaks on refactor) -->
<ol class="concert-scroll date-group-list">

<!-- AFTER: data-testid (stable across refactors) -->
<ol class="concert-scroll date-group-list" data-testid="concert-scroll">
```

```typescript
// BEFORE: Fragile CSS class selector
const scroll = page.locator('.concert-scroll')

// AFTER: Stable test ID selector
const scroll = page.getByTestId('concert-scroll')
```

**Scope — Phase 1 critical selectors to migrate:**

| Current Selector | Component | data-testid |
|-----------------|-----------|-------------|
| `.concert-scroll` | concert-highway | `concert-scroll` |
| `[data-live-card]` | event-card | (already stable) |
| `.journey-badge` | event-card | `journey-badge` |
| `.sheet-journey` | event-detail-sheet | `sheet-journey` |
| `.journey-btn` | event-detail-sheet | `journey-btn` |
| `.journey-remove-btn` | event-detail-sheet | `journey-remove-btn` |
| `.loading-text` | dashboard-route | `dashboard-loading` |
| `.welcome-preview` | welcome-route | `welcome-preview` |

**Convention:** `data-testid` values use kebab-case matching the component/semantic purpose, not CSS class names. Only add to elements actually used in E2E tests — not every element.

### Decision 4: Fix application-layer issues causing page.evaluate() workarounds

**Choice:** Fix the root causes in application code rather than keeping test workarounds.

**Issue A: page-help dismiss-zone intercepts pointer events**

The `page-help` component creates a full-viewport dismiss zone that captures all click events. E2E tests must use `page.evaluate(() => el.click())` to bypass it.

**Fix:** Add `pointer-events: none` to the dismiss zone when the help overlay is not actively shown, and use `pointer-events: auto` only when visible:

```css
/* page-help.css */
.dismiss-zone {
  pointer-events: none;  /* default: transparent to clicks */
}

.dismiss-zone[data-active="true"] {
  pointer-events: auto;  /* only intercept when help is shown */
}
```

**Issue B: Popover top-layer blocks Playwright hit-testing**

Popover elements in the top layer intercept Playwright's actionability checks even when visually non-overlapping due to top-layer stacking.

**Fix:** Ensure popovers are closed (removed from top layer) before E2E assertions on elements behind them. In serial mode tests, add explicit popover dismiss before each interaction:

```typescript
// In E2E beforeEach for serial tests
await page.evaluate(() => {
  document.querySelectorAll('[popover]').forEach(el => {
    try { (el as HTMLElement).hidePopover() } catch {}
  })
})
```

**Issue C: visually-hidden radio inputs**

Radio inputs with `class="visually-hidden"` are not clickable by Playwright (zero bounding box).

**Fix per [Playwright docs](https://playwright.dev/docs/actionability#visible):** Use `force: true` on the label click, or use Playwright's `page.getByLabel()` which clicks the associated label:

```typescript
// BEFORE: JS dispatch workaround
await page.evaluate(() => {
  const radio = document.querySelector('input[type="radio"]')
  radio.dispatchEvent(new Event('change', { bubbles: true }))
})

// AFTER: Click the visible label
await page.getByLabel('日本語').click()
```

### Decision 5: CE composition integration tests via createFixture

**Choice:** Create integration tests that mount parent CE containing child CEs to verify layout propagation, using `createFixture` from `@aurelia/testing`.

**Rationale (per [Aurelia Testing Components](https://docs.aurelia.io/developer-guides/overview/testing-components)):**
The official docs recommend testing "view and view-model together." For CE composition, this means mounting the parent with its child CEs registered:

```typescript
import { createFixture, Registration } from '@aurelia/testing'
import { ConcertHighway } from '../../src/components/live-highway/concert-highway'
import { EventCard } from '../../src/components/event-card/event-card'

it('concert-highway renders with non-zero height when dateGroups provided', async () => {
  const fixture = await createFixture
    .component(class App {
      dateGroups = [mockDateGroup]
    })
    .html`<div style="display:grid; grid-template-rows: auto 1fr; height:500px">
      <concert-highway date-groups.bind="dateGroups"></concert-highway>
    </div>`
    .deps(ConcertHighway, EventCard)
    .build()
    .started

  const ce = fixture.getBy('concert-highway')
  expect(ce.offsetHeight).toBeGreaterThan(0)

  await fixture.stop(true)
})
```

**Key composition scenarios to test:**
1. `dashboard-route` + `concert-highway` — grid height propagation
2. `welcome-route` + `concert-highway` — scroll-snap overflow containment
3. `concert-highway` + `event-card` — subgrid lane alignment

**JSDOM limitation:** `offsetHeight` and computed styles may not fully replicate browser layout. Tests should verify DOM structure and CSS class/attribute presence. For pixel-accurate layout, E2E remains necessary — but composition tests catch structural issues (missing elements, broken bindings, incorrect display modes).

### Decision 6: Dashboard-route integration test

**Choice:** Create `test/routes/dashboard-route.fixture.spec.ts` using `createFixture` with all 3 service mocks.

**Rationale:** Dashboard-route is the most complex route component with:
- `IConcertService`, `IFollowServiceClient`, `ITicketJourneyService` (3 service injections)
- `isLoading` / `loadError` / `dateGroups` / `needsRegion` / `showCelebration` (5 state flags)
- 6 child CEs in its template

The previous `dashboard-route.spec.ts` was deleted during PR #298 due to Unhandled Rejection from the module chain explosion. With Decision 2's containment strategy, it can be safely reintroduced:

```typescript
// Mock the HTML template to prevent child CE chain loading
vi.mock('../../src/routes/dashboard/dashboard-route.html', () => ({
  default: `
    <p if.bind="isLoading" data-testid="dashboard-loading">Loading</p>
    <div if.bind="!isLoading && !loadError && dateGroups.length > 0"
         data-testid="concert-content">Content</div>
  `
}))

import { DashboardRoute } from '../../src/routes/dashboard/dashboard-route'

it('shows loading state initially', async () => {
  const mockConcertService = { listWithProximity: vi.fn().mockResolvedValue({ groups: [] }) }

  const fixture = await createFixture
    .component(DashboardRoute)
    .html`<dashboard-route></dashboard-route>`
    .deps(
      Registration.instance(IConcertService, mockConcertService),
      Registration.instance(IFollowServiceClient, mockFollowService),
      Registration.instance(ITicketJourneyService, mockJourneyService),
    )
    .build()
    .started

  // isLoading should be false after attached() completes
  expect(mockConcertService.listWithProximity).toHaveBeenCalled()
  await fixture.stop(true)
})
```

### Decision 7: Evaluate vitest environment optimization

**Choice:** Evaluate and adopt optimizations in phases.

**Phase A: Per-file environment annotations (immediate)**

Per [Vitest docs](https://vitest.dev/guide/environment.html#environments-for-specific-files), use control comments to run pure logic tests in `node` environment:

```typescript
// test/adapter/rpc/mapper/artist-mapper.spec.ts
// @vitest-environment node

import { describe, it, expect } from 'vitest'
// ... pure mapping logic tests, no DOM needed
```

This avoids jsdom initialization overhead for ~30 test files that don't need DOM.

**Phase B: happy-dom evaluation (spike)**

Per vitest docs: "happy-dom is considered to be faster than jsdom, but lacks some API."

Run benchmark:
```bash
# Compare test execution time
time npx vitest run --environment jsdom
time npx vitest run --environment happy-dom
```

Evaluate:
- Does Aurelia's `BrowserPlatform` work with happy-dom?
- Do `createFixture` tests pass with happy-dom?
- What's the speed improvement?

**Phase C: vitest projects (future consideration)**

Per [Vitest Projects docs](https://vitest.dev/guide/#projects-support):
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          environment: 'node',
          include: ['test/adapter/**', 'test/entities/**', 'test/services/**'],
        },
      },
      {
        test: {
          name: 'integration',
          environment: 'jsdom',  // or happy-dom
          include: ['test/components/**', 'test/routes/**', 'test/smoke/**'],
          setupFiles: ['./test/setup.ts'],
        },
      },
    ],
  },
})
```

This is a larger refactor and may be deferred if Phase A + B yield sufficient improvement.

## Risks / Trade-offs

### [Risk] Removing manual JSDOM breaks tests that depend on specific JSDOM configuration
**Mitigation:** The current manual JSDOM uses `url: 'http://localhost'` — vitest's jsdom environment defaults to the same. Run full test suite after change to verify. If specific JSDOM options are needed, they can be passed via `environmentOptions.jsdom` in `vitest.config.ts` per [Vitest docs](https://vitest.dev/guide/environment.html).

### [Risk] data-testid attributes add maintenance burden to templates
**Mitigation:** Only add to elements actually used in E2E tests (~15-20 elements total). The attribute is inert and doesn't affect rendering or accessibility. Convention: `data-testid` is only added when an E2E test references the element.

### [Risk] Template HTML mocking (Decision 2, Pillar C) may mask template binding errors
**Mitigation:** Template mocking is only used for route-level tests where the goal is testing ViewModel logic. Template binding correctness is verified by the `createFixture` component integration tests from `refine-frontend-testing` (PR #360). The two approaches are complementary.

### [Risk] happy-dom may not support all APIs used by Aurelia
**Mitigation:** This is explicitly a spike/evaluation, not a commitment. If happy-dom fails, jsdom remains the default. Per vitest docs, per-file `// @vitest-environment jsdom` can override for specific files that need full jsdom.

### [Trade-off] page-help pointer-events fix changes visible behavior
**Accepted:** The dismiss-zone should be transparent when the help overlay is not shown. The current behavior (always intercepting) is a bug, not a feature. Users are not affected because the overlay is invisible when inactive.

### [Trade-off] Two CE testing patterns coexist (composition + unit)
**Accepted:** CE composition tests verify parent-child layout. CE unit tests (from `refine-frontend-testing`) verify individual component logic. Both are needed — this is the same unit/integration split recommended by the Aurelia docs.
