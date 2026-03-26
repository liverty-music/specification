## Context

The frontend test suite was built with a "DI Unit tests as PRIMARY" strategy documented in `docs/testing-strategy.md`. This served the team well for rapid initial coverage, achieving ~55% statement coverage. However, a thorough review of the [Aurelia 2 official testing documentation](https://docs.aurelia.io/developer-guides/overview) reveals that the framework provides a rich integration testing API via `@aurelia/testing` that the project underutilizes.

**Current state:**
- 58+ unit test files, mostly DI container + method invocation pattern
- `createFixture` used only in 1 smoke test file with tautological assertions (`expect(true).toBe(true)`)
- `@aurelia/testing` provides 20+ fixture helper methods (assertText, trigger.click, getBy, etc.) — none actively used
- `auth-service.ts` excluded from coverage due to module-level `window.location` access
- Dead vitest config pattern (`src/*-page.ts`) matches no files
- Template binding bugs (typos, broken expressions) only caught at E2E layer

**Audit findings (infrastructure bugs):**
- `test/setup.ts:50` — `forEach(async)` pattern silently breaks fixture cleanup (Promises not awaited)
- `test/smoke/component-compile.spec.ts` — uses deprecated `tearDown()` instead of `stop(true)`
- 2 test files missing `localStorage.clear()` in `afterEach` (state pollution between tests)
- 5 test files have `vi.useRealTimers()` inside `it()` blocks instead of `afterEach` (timer state leak)
- 3 mock helpers lack proper return types (untyped `any` instead of `Partial<IInterface>`)
- `auth-service.spec.ts` accesses private members via `@ts-expect-error` instead of testing public API
- Only 6% of components (2/33) have any `createFixture` test; 30% (10/33) have no test at all

**Aurelia 2 Official Testing Documentation** (all pages referenced in this design):

| Page | URL | Relevance |
|------|-----|-----------|
| Testing Overview | [developer-guides/overview](https://docs.aurelia.io/developer-guides/overview) | Platform setup, TestContext, core concepts |
| Getting Started | [developer-guides/overview (Testing section)](https://docs.aurelia.io/developer-guides/overview) | bootstrapTestEnvironment, configuration |
| Testing Components | [developer-guides/overview/testing-components](https://docs.aurelia.io/developer-guides/overview/testing-components) | createFixture patterns, DOM assertions, event testing |
| Testing Attributes | [developer-guides/overview/testing-attributes](https://docs.aurelia.io/developer-guides/overview/testing-attributes) | Custom attribute testing via createFixture |
| Testing Value Converters | [developer-guides/overview/testing-value-converters](https://docs.aurelia.io/developer-guides/overview/testing-value-converters) | Unit + integration test combination |
| Working with the Fluent API | [developer-guides/overview/fluent-api](https://docs.aurelia.io/developer-guides/overview/fluent-api) | Builder pattern for createFixture |
| Stubs, Mocks & Spies | [developer-guides/overview/mocks-spies](https://docs.aurelia.io/developer-guides/overview/mocks-spies) | DI mocking via Registration, spy patterns |
| Advanced Testing Techniques | [developer-guides/overview/advanced-testing](https://docs.aurelia.io/developer-guides/overview/advanced-testing) | Async patterns, lifecycle, accessibility, drag-and-drop |
| Outcome Recipes | [developer-guides/overview/outcome-recipes](https://docs.aurelia.io/developer-guides/overview/outcome-recipes) | API calls, router, form validation, component interaction, lifecycle hooks, real-world dependencies |
| Quick Reference | [developer-guides/overview (Testing section)](https://docs.aurelia.io/developer-guides/overview) | API cheat sheet, troubleshooting |
| Decision Trees | [developer-guides/overview (Testing section)](https://docs.aurelia.io/developer-guides/overview) | When to use which test approach |

## Goals / Non-Goals

**Goals:**
- Fix critical test infrastructure bugs (forEach+async cleanup, deprecated tearDown, localStorage pollution, timer state leak)
- Align the testing strategy with Aurelia 2 official documentation by adopting `createFixture` as a co-primary test approach
- Add component integration tests for critical-path components that verify template bindings and DOM interactions
- Upgrade smoke tests to use meaningful fixture assertions instead of tautologies
- Improve mock helper type safety to prevent runtime type errors
- Make `auth-service.ts` testable by refactoring away module-level browser global access
- Clean up dead vitest configuration
- Update `docs/testing-strategy.md` to reflect the new approach
- Incrementally raise coverage thresholds

**Non-Goals:**
- Replacing all existing DI Unit tests with fixture tests (DI Unit tests remain valid for pure logic)
- Adding new E2E tests (existing Playwright coverage is sufficient)
- Refactoring component source code beyond what's needed for testability
- Achieving 100% coverage

## Decisions

### Decision 1: Elevate `createFixture` to co-primary status

**Choice:** `createFixture` integration tests become the **default for components** that have templates; DI Unit tests remain the default for services and pure logic.

**Rationale (per official docs):**
- [Testing Components](https://docs.aurelia.io/developer-guides/overview/testing-components): "Aurelia 2 uses integration testing that covers both the view and view model together"
- [Outcome Recipes](https://docs.aurelia.io/developer-guides/overview/outcome-recipes): All 6 recipes use `createFixture`, including router testing, form validation, lifecycle hooks, and component interaction
- [Advanced Testing](https://docs.aurelia.io/developer-guides/overview/advanced-testing): Fixture API provides specialized validators for text, HTML, attributes, classes, styles, and form values

**Updated decision flow:**

```
Is it a pure function with no dependencies?
├── YES → Pure Unit Test
│
└── NO → Is it a component with a template?
         ├── YES → Component Integration Test (createFixture)    ★ CHANGED
         │         Use: assertText, trigger.click, getBy, type()
         │         DI mocking via Registration.instance() in deps
         │
         └── NO → Is it a service, interceptor, or guard?
                  ├── YES → DI Unit Test (createTestContainer)
                  │
                  └── NO → E2E Test (Playwright)
```

**Alternative considered:** Keep DI Unit as primary for all modules, add fixture tests only for specific binding-heavy components.
**Why rejected:** The official documentation explicitly recommends view+view-model integration testing as the standard approach. Limiting fixture tests to "specific cases" would perpetuate the gap.

### Decision 2: Use the Fluent Builder API for new fixture tests

**Choice:** All new `createFixture` tests use the fluent builder pattern.

**Rationale (per [Fluent API docs](https://docs.aurelia.io/developer-guides/overview/fluent-api)):**

```typescript
// PREFERRED: Fluent builder (better type inference, readable)
const fixture = await createFixture
  .component(BottomNavBar)
  .html`<bottom-nav-bar></bottom-nav-bar>`
  .deps(
    Registration.instance(IRouter, mockRouter),
    Registration.instance(IAuthService, mockAuth),
  )
  .build()
  .started

// LEGACY: Single call (still valid but less readable)
const { appHost } = createFixture(
  '<bottom-nav-bar></bottom-nav-bar>',
  class App {},
  [BottomNavBar, Registration.instance(IRouter, mockRouter)]
)
```

Benefits per docs: "better TypeScript support with proper type inference for components" and "template interpolation with tagged template literals."

### Decision 3: Adopt official fixture assertion helpers

**Choice:** Use `IFixture` assertion methods instead of raw DOM queries.

**Rationale (per [Testing Components](https://docs.aurelia.io/developer-guides/overview/testing-components) and [Advanced Testing](https://docs.aurelia.io/developer-guides/overview/advanced-testing)):**

| Official API | Replaces | Benefit |
|---|---|---|
| `fixture.assertText('selector', 'text')` | `expect(el.textContent).toBe(...)` | Null-safe, whitespace handling |
| `fixture.assertAttr('sel', 'name', 'val')` | `expect(el.getAttribute(...)).toBe(...)` | Focused error messages |
| `fixture.assertClass('sel', 'active')` | `expect(el.classList.contains(...)).toBe(true)` | Multi-class support |
| `fixture.assertValue('input', 'val')` | `expect((el as HTMLInputElement).value).toBe(...)` | Type-safe |
| `fixture.getBy('selector')` | `appHost.querySelector(...)` | Throws if 0 or >1 match |
| `fixture.queryBy('selector')` | `appHost.querySelector(...)` | Explicit null return |
| `fixture.trigger.click('button')` | Manual event dispatch | Full event init support |
| `fixture.type('input', 'text')` | Manual value set + dispatchEvent | Triggers binding update |

### Decision 4: Use `tasksSettled()` for reactive updates

**Choice:** After mutating component state, always `await tasksSettled()` before DOM assertions.

**Rationale (per [Outcome Recipes](https://docs.aurelia.io/developer-guides/overview/outcome-recipes) and [Quick Reference](https://docs.aurelia.io/developer-guides/overview)):**

```typescript
// Official pattern for async state changes
component.items.push('new item')
await tasksSettled()  // Wait for Aurelia to process the change queue
fixture.assertText('.count', '4')
```

This replaces ad-hoc `await new Promise(r => setTimeout(r, 0))` or missing sync waits.

### Decision 5: Refactor auth-service.ts with lazy initialization

**Choice:** Move `UserManagerSettings` construction from module scope to a lazy getter inside `AuthService`.

**Rationale (per [Stubs, Mocks & Spies](https://docs.aurelia.io/developer-guides/overview/mocks-spies)):**
The official docs show all dependencies resolved via `resolve()` at class instantiation time, not at module parse time. The current module-level `window.location.origin` access violates this pattern and prevents both testing and coverage.

```typescript
// BEFORE: Module-level (untestable)
const settings: UserManagerSettings = {
  redirect_uri: `${window.location.origin}/auth/callback`,  // runs at import
}

// AFTER: Lazy initialization (testable)
export class AuthService {
  private _userManager: UserManager | undefined

  private get userManager(): UserManager {
    if (!this._userManager) {
      this._userManager = new UserManager({
        redirect_uri: `${window.location.origin}/auth/callback`,
        // ... other settings
      })
      this.subscribeToEvents()
    }
    return this._userManager
  }
}
```

**Alternative considered:** DI-inject a config object from `main.ts`.
**Why rejected:** More invasive change with breaking API. Lazy init is minimal and keeps the same public surface.

### Decision 6: Upgrade smoke tests with real assertions

**Choice:** Replace `expect(true).toBe(true)` with meaningful fixture assertions.

**Rationale (per [Testing Components](https://docs.aurelia.io/developer-guides/overview/testing-components)):**

```typescript
// BEFORE: Proves nothing
const { tearDown } = await createFixture('<svg-icon name="home"></svg-icon>', {}, [...]).started
expect(true).toBe(true)
await tearDown()

// AFTER: Proves template compiled AND rendered correctly
const fixture = await createFixture
  .component(class App { iconName = 'home' })
  .html`<svg-icon name.bind="iconName"></svg-icon>`
  .deps(SvgIcon, ...sharedRegistrations)
  .build()
  .started

fixture.assertAttr('svg-icon', 'data-icon', 'home')
await fixture.stop(true)
```

### Decision 7: Test lifecycle hooks via `.started` and `stop(true)`

**Choice:** Use the official lifecycle testing pattern from [Outcome Recipes - Recipe 5](https://docs.aurelia.io/developer-guides/overview/outcome-recipes).

**Rationale:**
```typescript
// Official pattern: .started waits for all async lifecycle hooks
const fixture = await createFixture
  .component(DashboardRoute)
  .html`<dashboard-route></dashboard-route>`
  .deps(Registration.instance(IDashboardService, mockService))
  .build()
  .started  // ← binding(), bound(), attaching(), attached() all complete

// Verify attached() side effects
expect(mockService.loadData).toHaveBeenCalledOnce()

// stop(true) triggers detaching() + unbinding()
await fixture.stop(true)
expect(mockService.cleanup).toHaveBeenCalledOnce()
```

### Decision 8: Mock services via Registration.instance() in fixture deps

**Choice:** Use `Registration.instance()` as the 3rd parameter (or via `.deps()`) per [Stubs, Mocks & Spies](https://docs.aurelia.io/developer-guides/overview/mocks-spies).

**Rationale:** This is the official Aurelia DI mocking pattern. It works for both `@inject` decorator and `resolve()` function patterns:

```typescript
const mockApi = { fetchData: vi.fn().mockResolvedValue([1, 2, 3]) }

const fixture = await createFixture
  .component(MyComponent)
  .html`<my-component></my-component>`
  .deps(
    MyComponent,
    Registration.instance(IApiService, mockApi),
    Registration.instance(IRouter, createMockRouter()),
  )
  .build()
  .started
```

Existing `test/helpers/mock-*.ts` factories remain valid — they produce the mock objects passed to `Registration.instance()`.

### Decision 9: Value converter tests combine unit + integration

**Choice:** Per [Testing Value Converters](https://docs.aurelia.io/developer-guides/overview/testing-value-converters), keep existing pure unit tests AND add fixture-based integration tests.

**Rationale:** "Good tests cover a range of scenarios" — unit tests verify converter logic; fixture tests verify the converter works within an Aurelia view pipeline (`${value | converter}`).

### Decision 10: Custom attribute tests use createFixture with style assertions

**Choice:** Per [Testing Attributes](https://docs.aurelia.io/developer-guides/overview/testing-attributes), test custom attributes by rendering them on host elements and verifying DOM mutations.

**Rationale:** Custom attributes modify element behavior/styling. The official pattern creates a fixture with the attribute applied, then asserts style/class/attribute changes:

```typescript
const fixture = await createFixture
  .component(class App { color = 'blue' })
  .html`<div tile-color="color.bind: color"></div>`
  .deps(TileColorCustomAttribute)
  .build()
  .started

fixture.assertStyles('div', { '--tile-color': 'blue' })
```

### Decision 11: Fix forEach+async fixture cleanup in setup.ts

**Choice:** Replace `fixtures.forEach(async (f) => ...)` with `for...of` loop inside an `async` afterEach.

**Rationale (per [Testing Components](https://docs.aurelia.io/developer-guides/overview/testing-components) — "Always call `stop(true)` for cleanup"):**

`Array.forEach` does not await async callbacks — the Promises fire but are never awaited. This means fixture teardown races with the next test's setup, causing cross-test contamination.

```typescript
// BEFORE: Promises not awaited (BUG)
afterEach(() => {
  fixtures.forEach(async (f) => {
    try { await f.stop(true) } catch { /* ignore */ }
  })
  fixtures.length = 0  // ← clears before stop() completes
})

// AFTER: Sequential cleanup with proper await
afterEach(async () => {
  await Promise.all(fixtures.map(f => f.stop(true).catch(() => {})))
  fixtures.length = 0
})
```

### Decision 12: Enforce afterEach hygiene across all test files

**Choice:** All test files SHALL follow these `afterEach` rules per [Quick Reference](https://docs.aurelia.io/developer-guides/overview):

1. `vi.restoreAllMocks()` — in every test suite that uses spies
2. `vi.useRealTimers()` — in every suite that uses `vi.useFakeTimers()`, never inside `it()` blocks
3. `localStorage.clear()` — in every suite that reads/writes localStorage
4. `fixture.stop(true)` — in every suite that creates fixtures (or handled by global setup.ts hook)

**Rationale:** The audit found 5 files with `vi.useRealTimers()` inside `it()` blocks (timer state leaks to subsequent tests) and 2 files missing `localStorage.clear()` in `afterEach` (state pollution). Per the official docs' troubleshooting section, these cause "property update delays" and "cleanup failures."

**Files to fix:**
- `test/services/pwa-install-service.spec.ts` — add `localStorage.clear()` to afterEach
- `test/components/notification-prompt.spec.ts` — add `localStorage.clear()` to afterEach
- `test/routes/discovery-route.spec.ts` — move `vi.useRealTimers()` to afterEach
- `test/routes/my-artists-route.spec.ts` — move `vi.useRealTimers()` to afterEach
- `test/services/connect-error-router.spec.ts` — move `vi.useRealTimers()` to afterEach
- `test/components/dna-orb-canvas.spec.ts` — move `vi.useRealTimers()` to afterEach
- `test/value-converters/date.spec.ts` — move `vi.useRealTimers()` to afterEach

### Decision 13: Type-safe mock helpers

**Choice:** All mock factories SHALL return `Partial<IInterface>` with explicit return types per [Stubs, Mocks & Spies](https://docs.aurelia.io/developer-guides/overview/mocks-spies).

**Rationale:** Three mock helpers currently return untyped objects:
- `mock-i18n.ts` — returns implicit `any`, should return `Partial<I18N>`
- `mock-toast.ts` — returns implicit `any`, should return `Partial<IEventAggregator>` or typed toast interface
- `mock-error-boundary.ts` — `currentError`/`errorHistory` are plain values instead of properly typed

Untyped mocks silently allow incorrect mock shapes to pass TypeScript compilation, leading to runtime failures that are hard to debug.

## Risks / Trade-offs

### [Risk] Fixture tests are slower than DI Unit tests
**Mitigation:** Only add fixture tests for components that benefit from template verification. Services and pure logic remain as DI Unit tests. The official docs note that `createFixture` creates an isolated mini-Aurelia context — it's lightweight compared to full app bootstrap.

### [Risk] `auth-service.ts` lazy init could change timing behavior
**Mitigation:** The `AuthService` is a singleton registered at app startup. The `ready` Promise already gates all consumers. Lazy init simply moves `UserManager` creation from module parse to first property access — consumers already await `ready` before using the service.

### [Risk] Existing DI Unit tests may become redundant with fixture tests
**Mitigation:** We explicitly do NOT replace existing passing tests. New fixture tests are additive, focusing on template binding verification that DI Unit tests cannot cover.

### [Risk] JSDOM limitations may cause fixture test failures
**Mitigation:** Some APIs (Canvas, `popover`, `showModal`) are not available in JSDOM. For components requiring these, retain the DI Unit test pattern with mocked `INode`. The [Advanced Testing](https://docs.aurelia.io/developer-guides/overview/advanced-testing) docs note that JSDOM is the standard environment; components with canvas dependencies are appropriately excluded.

### [Trade-off] Two test patterns coexist
**Accepted:** DI Unit tests for services/interceptors/guards + `createFixture` tests for components with templates. This is exactly the split the official docs recommend — each pattern serves a distinct purpose.
