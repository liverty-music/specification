# Frontend Testing Methodology Review

Comprehensive assessment of the current test suite against modern best practices (2025-2026), with module-specific optimal testing strategy recommendations.

## Executive Summary

The current test suite follows a **DI-container-only approach** consistently across all 37 test files. This approach is effective, fast, and well-suited for the Aurelia 2 architecture. However, several areas can be improved to align with the latest best practices. This document provides:

1. **Assessment** of current patterns against industry standards
2. **Module-by-module** optimal testing strategy recommendations
3. **Actionable improvements** prioritized by impact

---

## Part 1: Current Patterns Assessment

### 1.1 What the Current Suite Does Well

| Practice | Status | Details |
|----------|--------|---------|
| DI-based test isolation | Excellent | `createTestContainer()` + `Registration.instance()` is idiomatic Aurelia 2 |
| Timer cleanup in `afterEach` | Fixed | Anti-pattern resolved; `vi.useRealTimers()` now in `afterEach` consistently |
| Mock helper centralization | Good | Typed `Partial<IInterface>` factories prevent inline mock duplication |
| AAA structure | Good | Most tests follow Arrange-Act-Assert implicitly |
| AbortSignal-aware mocking | Good | Signal-aware mocks properly reject on abort (loading-sequence-service) |
| Fake timer async API | Good | Uses `vi.advanceTimersByTimeAsync()` (promise-safe) |
| Error scenario coverage | Good | Tests cover success, partial failure, complete failure, abort, and retry |

### 1.2 Areas for Improvement

#### ISSUE 1: Heavy reliance on `vi.mock()` (HIGH)

**Current**: 20+ test files use `vi.mock()` at file scope for module replacement.

**Problem**: `vi.mock()` is hoisted to the top of the file, replaces the **entire module**, and creates a hidden coupling between test file structure and mock setup. This is a known footgun:
- Tests become order-dependent within a file
- Partial mocking is difficult
- Mock state leaks between tests if not carefully reset

**Best Practice (2025)**: Prefer `vi.spyOn()` for targeted mocking. Use `vi.mock()` only when module-level side effects make it unavoidable (e.g., `auth-service.ts` reads `window.location` at parse time).

**Assessment**: In this project, `vi.mock()` is **justified** for modules with import-time side effects (proto imports, auth-service). For other cases, it is used as a convenience pattern rather than a necessity. The `vi.mock()` + dynamic `await import()` pattern is well-established in the codebase and works reliably, so the cost of migrating away is not worth it for existing tests. **New tests should prefer `vi.spyOn()` where feasible.**

#### ISSUE 2: No DOM/template binding verification (MEDIUM)

**Current**: All tests exercise class logic directly. No tests verify that template bindings (`if.bind`, `repeat.for`, `click.trigger`) work correctly.

**Best Practice**: Kent C. Dodds' Testing Trophy model emphasizes **integration tests** (components rendered with real DOM) as the primary test layer.

**Assessment**: For this project, the DI-only approach is a **pragmatic trade-off**. The testable behavior (URL construction, state transitions, API calls) is accessible through public methods. Template binding bugs are low-frequency and better caught by:
- TypeScript template checking (Aurelia 2 supports this)
- Visual review via Storybook
- E2E tests (Playwright, planned)

**Recommendation**: Keep DI-only for unit tests. Add a small number of `createFixture()` integration tests for critical user flows (auth redirect, loading sequence, error display) in a future phase.

#### ISSUE 3: No Page Object Model (POM) abstraction (LOW)

**Current**: Test files directly access `sut` properties and call methods inline.

**Best Practice**: POM separates "what to test" from "how to interact". Useful for E2E and complex component tests.

**Assessment**: POM is **not needed** for DI-only unit tests. The current approach is simpler and more maintainable at this scale. POM should be adopted when E2E tests (Playwright) are introduced.

#### ISSUE 4: Replicated pure functions in proof-service tests (LOW)

**Current**: `bytesToHex`, `bytesToDecimal`, `uuidToFieldElement` are **copied** into the test file because they are not exported from the source module.

**Best Practice**: Test public APIs. If functions are worth testing, they should be exported.

**Recommendation**: Export these utility functions from `proof-service.ts` or extract to a `proof-utils.ts` module, then import directly in tests.

#### ISSUE 5: `as any` type casts in mock usage (LOW)

**Current**: Several tests use `as any` to bypass TypeScript when passing mock objects.

**Best Practice**: Typed mocks via `Partial<T>` should eliminate the need for `as any`.

**Assessment**: Most mock helpers already return `Partial<T>`. The `as any` casts appear where Aurelia's DI container expects exact types. This is a minor code quality issue, not a reliability concern.

---

## Part 2: Module-Specific Optimal Testing Strategies

### Legend
- **DI-Unit**: Test via `createTestContainer()` + direct method invocation
- **Fixture-Integration**: Test via `@aurelia/testing` `createFixture()` with DOM rendering
- **Pure-Unit**: Test pure functions directly (no DI container needed)
- **Interceptor**: Test via mock `next()` function pattern
- **POM-E2E**: Page Object Model with Playwright (future)

---

### 2.1 Services

| Module | Current Pattern | Optimal Pattern | Gap | Priority |
|--------|----------------|-----------------|-----|----------|
| `auth-service.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Justified (window.location at import) | - |
| `artist-discovery-service.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Justified (proto imports) | - |
| `concert-service.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Justified (proto imports) | - |
| `ticket-service.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Same pattern needed | - |
| `loading-sequence-service.ts` | DI-Unit + fake timers | DI-Unit + fake timers | Already optimal | - |
| `error-boundary-service.ts` | DI-Unit (no vi.mock) | DI-Unit (no vi.mock) | Already optimal | - |
| `dashboard-service.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Justified (proto imports) | - |
| `proof-service.ts` | Pure-Unit (replicated) | Pure-Unit (exported) | Export utility functions | Low |
| `grpc-transport.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Justified (factory pattern) | - |
| `connect-error-router.ts` | Interceptor + fake timers | Interceptor + fake timers | Already optimal | - |
| `toast-notification.ts` | DI-Unit + fake timers + RAF | DI-Unit + fake timers + RAF | Already optimal | - |
| `notification-manager.ts` | Not tested | DI-Unit + navigator mock | New test needed | P3 |
| `push-service.ts` | Not tested | DI-Unit + SW mock + fake timers | New test needed | P4 |
| `global-error-handler.ts` | Not tested | DI-Unit + window mock | New test needed | P3 |
| `otel-init.ts` | Not tested | Isolated function test | Low value | P4 |

### 2.2 Route Components

| Module | Current Pattern | Optimal Pattern | Gap | Priority |
|--------|----------------|-----------------|-----|----------|
| `loading-sequence` (route) | DI-Unit + vi.mock | DI-Unit + vi.mock | Already optimal | - |
| `dashboard.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Already optimal | - |
| `discover-page.ts` | DI-Unit + vi.mock + fake timers | DI-Unit + vi.mock + fake timers | Already optimal | - |
| `artist-discovery-page.ts` | DI-Unit + vi.mock + fake timers | DI-Unit + vi.mock + fake timers | Already optimal | - |
| `tickets-page.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Already optimal | - |
| `my-artists-page.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Already optimal | - |
| `auth-callback.ts` | DI-Unit + vi.mock | DI-Unit + vi.mock | Already optimal | - |
| `welcome-page.ts` | Not tested | DI-Unit + auth mock | Simple test | P3 |
| `settings-page.ts` | Not tested | DI-Unit | Low complexity | P4 |
| `about-page.ts` | Not tested | DI-Unit | Minimal logic | P4 |
| `not-found-page.ts` | Not tested | DI-Unit | Trivial | P4 |

### 2.3 UI Components

| Module | Current Pattern | Optimal Pattern | Gap | Priority |
|--------|----------------|-----------------|-----|----------|
| `event-detail-sheet.ts` | DI-Unit + INode mock | DI-Unit + INode mock | Already optimal | - |
| `event-card.ts` | DI-Unit + INode mock | DI-Unit + INode mock | Already optimal | - |
| `live-highway.ts` | DI-Unit | DI-Unit | Already optimal | - |
| `auth-status.ts` | DI-Unit | DI-Unit | Already optimal | - |
| `area-selector-sheet.ts` | DI-Unit + INode mock | DI-Unit + INode mock | Already optimal | - |
| `dna-orb-canvas.ts` | Not tested | **Deferred** (Canvas/RAF/Matter.js) | Complex setup | Deferred |
| `bubble-physics.ts` | Not tested | **Deferred** (Matter.js lazy load) | Complex setup | Deferred |
| `region-setup-sheet.ts` | Not tested | DI-Unit + INode mock | New test | P3 |
| `notification-prompt.ts` | Not tested | DI-Unit + permission mock | New test | P3 |
| `error-banner.ts` | Not tested | DI-Unit (trivial) | Minimal logic | P4 |

### 2.4 Hooks & Value Converters

| Module | Current Pattern | Optimal Pattern | Gap | Priority |
|--------|----------------|-----------------|-----|----------|
| `auth-hook.ts` | DI-Unit + async ready | DI-Unit + async ready | Already optimal | - |
| `date.ts` (value converter) | Pure-Unit + fake timers | Pure-Unit + fake timers | Already optimal | - |

### 2.5 Root & Config

| Module | Current Pattern | Optimal Pattern | Gap | Priority |
|--------|----------------|-----------------|-----|----------|
| `my-app.ts` | DI-Unit + router mock | DI-Unit + router mock | Already optimal | - |
| `main.ts` | Not tested (excluded) | Not unit-testable | Correctly excluded | - |

---

## Part 3: Testing Pattern Reference by Module Characteristics

### Pattern A: DI-Registered Service (Standard)

**When to use**: Service with injected dependencies, no import-time side effects.

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { DI, Registration } from 'aurelia'
import { createTestContainer } from '../helpers/create-container'

describe('MyService', () => {
  let sut: MyService
  let mockDep: Partial<IDependency>

  beforeEach(() => {
    mockDep = {
      doSomething: vi.fn().mockResolvedValue('result'),
    }
    const container = createTestContainer(
      Registration.instance(IDependency, mockDep),
    )
    container.register(MyService)
    sut = container.get(IMyService)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should delegate to dependency', async () => {
    // Arrange
    mockDep.doSomething!.mockResolvedValue('custom')

    // Act
    const result = await sut.process()

    // Assert
    expect(result).toBe('custom')
    expect(mockDep.doSomething).toHaveBeenCalledOnce()
  })
})
```

**Best practices**:
- Use `Partial<IInterface>` for type-safe mocks
- One `beforeEach` for container setup, one `afterEach` for cleanup
- Each test overrides only what it needs

---

### Pattern B: Service with Import-Time Side Effects

**When to use**: Module imports proto-generated clients, reads `window.location`, or has other parse-time effects.

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { DI, Registration } from 'aurelia'
import { createTestContainer } from '../helpers/create-container'

// Step 1: Mock modules BEFORE any import
const mockIAuthService = DI.createInterface('IAuthService')
vi.mock('../../src/services/auth-service', () => ({
  IAuthService: mockIAuthService,
}))

vi.mock('@buf/liverty-music_schema.connectrpc_es/...', () => ({
  SomeService: { typeName: 'MockService' },
}))

vi.mock('@connectrpc/connect', () => ({
  createClient: vi.fn(),
}))

// Step 2: Dynamic import AFTER mocks are in place
const { MyServiceClass, IMyService } = await import('../../src/services/my-service')

describe('MyService', () => {
  // ... standard DI-Unit test
})
```

**When `vi.mock()` is justified**:
- Proto-generated imports (`@buf/liverty-music_schema.*`)
- `auth-service.ts` (reads `window.location.origin` at parse time)
- `grpc-transport.ts` (factory with complex dependencies)

**When `vi.mock()` is NOT justified**:
- Pure utility functions
- Services with no import side effects
- Components that only use DI-injected dependencies

---

### Pattern C: Interceptor / Higher-Order Function

**When to use**: gRPC interceptors, middleware, decorators.

```typescript
describe('createMyInterceptor', () => {
  it('should transform the request', async () => {
    // Arrange
    const response = { data: 'ok' }
    const next = vi.fn().mockResolvedValue(response)
    const interceptor = createMyInterceptor(config)
    const handler = interceptor(next)

    // Act
    const result = await handler(makeRequest())

    // Assert
    expect(result).toBe(response)
    expect(next).toHaveBeenCalledWith(
      expect.objectContaining({ header: expect.any(Headers) }),
    )
  })
})
```

**Best practices**:
- Test the interceptor in isolation from the transport
- Use `vi.fn()` as the `next` function
- Test both success and error paths
- For retry interceptors: use fake timers + `advanceTimersByTimeAsync()`

---

### Pattern D: Timer-Based Orchestration

**When to use**: Services with timeouts, debounce, animation timing.

```typescript
describe('TimerService', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('should timeout after 10 seconds', async () => {
    // Arrange: Use signal-aware mocks for AbortController scenarios
    mockDep.slowOperation = vi.fn().mockImplementation(
      (_arg: string, signal?: AbortSignal) =>
        new Promise((_resolve, reject) => {
          if (signal?.aborted) {
            reject(new DOMException('aborted', 'AbortError'))
            return
          }
          signal?.addEventListener('abort', () => {
            reject(new DOMException('aborted', 'AbortError'))
          })
        }),
    )

    // Act
    const promise = sut.aggregateData()
    await vi.advanceTimersByTimeAsync(10000)

    // Assert
    const result = await promise
    expect(result.status).toBe('failed')
  })
})
```

**Critical rules**:
- ALWAYS use `vi.advanceTimersByTimeAsync()` (not sync version) to avoid promise/timer deadlock
- ALWAYS restore real timers in `afterEach()`
- ALWAYS make mocks signal-aware when testing abort scenarios
- Use `.catch((err) => err)` pattern to prevent unhandled rejection errors

---

### Pattern E: AbortController / AbortSignal

**When to use**: Services that accept or create AbortSignals.

```typescript
it('should forward abort signal to backend', async () => {
  const controller = new AbortController()

  // Act
  const promise = sut.listConcerts('artist-1', controller.signal)
  controller.abort()

  // Assert
  await expect(promise).rejects.toThrow()
  expect(mockClient.list).toHaveBeenCalledWith(
    expect.anything(),
    expect.objectContaining({ signal: controller.signal }),
  )
})
```

---

### Pattern F: Pure Utility Functions

**When to use**: Math functions, formatters, converters with no side effects.

```typescript
describe('bytesToHex', () => {
  it.each([
    [new Uint8Array([255, 0, 171]), 'ff00ab'],
    [new Uint8Array([0]), '00'],
    [new Uint8Array([]), ''],
  ])('converts %o to "%s"', (input, expected) => {
    expect(bytesToHex(input)).toBe(expected)
  })
})
```

**Best practices**:
- Use `it.each()` for parameterized tests (table-driven)
- No DI container needed
- No mocks needed
- Test edge cases: empty input, single element, boundary values

---

### Pattern G: Component with INode (DOM Access)

**When to use**: Custom elements that query the DOM via `INode`.

```typescript
describe('EventDetailSheet', () => {
  let sut: EventDetailSheet
  let mockElement: HTMLElement

  beforeEach(async () => {
    mockElement = document.createElement('div')
    const scrollChild = document.createElement('div')
    scrollChild.classList.add('overflow-y-auto')
    mockElement.appendChild(scrollChild)

    const container = createTestContainer(
      Registration.instance(INode, mockElement),
    )
    container.register(EventDetailSheet)
    sut = container.get(EventDetailSheet)
  })
})
```

**Best practices**:
- Create a realistic DOM structure that matches the component's template queries
- Use `document.createElement()` (jsdom provides this)
- Test computed properties and event handlers, not template bindings

---

## Part 4: Comparison with Industry Best Practices

### 4.1 Kent C. Dodds Testing Trophy vs Our Approach

```
                 Testing Trophy              Our Approach
                 ═══════════════             ════════════
                    ┌─────┐                    ┌─────┐
       E2E         │  E2E │                    │  -- │  (planned, not yet)
                    ├─────┤                    ├─────┤
                    │     │                    │     │
   Integration     │█████│  ← PRIMARY         │  -- │  (no createFixture tests)
                    │█████│                    │     │
                    ├─────┤                    ├─────┤
                    │     │                    │█████│
       Unit        │ ███ │                    │█████│  ← ALL tests are here
                    │     │                    │█████│
                    ├─────┤                    ├─────┤
      Static       │█████│                    │█████│  TypeScript + ESLint
                    └─────┘                    └─────┘
```

**Gap**: The Testing Trophy recommends integration tests as the primary layer. Our suite is entirely unit tests.

**Assessment**: This is an **acceptable trade-off** for this project because:
1. Aurelia 2's DI system makes class-level tests highly representative of real behavior
2. The `resolve()` pattern means dependencies are real DI contracts, not arbitrary mocks
3. Template binding bugs are rare and better caught by Storybook + E2E
4. The 5-10x speed advantage of DI-only tests enables fast CI feedback

**Future recommendation**: Add a thin integration layer using `createFixture()` for:
- Auth flow (login redirect → callback → dashboard)
- Loading sequence (animation phases → navigation)
- Error boundary (error capture → banner display → GitHub issue link)

### 4.2 Testing Library Philosophy vs Our Approach

Testing Library advocates: *"Test the way users use the software."*

Our approach tests **class behavior** (method calls, property values), not **user behavior** (clicks, text visibility).

**Assessment**: For DI-only tests, this is inherent. The Testing Library philosophy applies to DOM-rendered tests. When `createFixture()` or E2E tests are added, adopt these query priorities:
1. `getByRole()` — semantic HTML
2. `getByLabelText()` — form inputs
3. `getByText()` — visible text
4. `getByTestId()` — last resort

### 4.3 Test Doubles Classification

| Double Type | Usage in Our Suite | Assessment |
|-------------|-------------------|------------|
| **Stub** (fixed return value) | `vi.fn().mockResolvedValue(...)` | Excellent — used everywhere |
| **Mock** (behavior verification) | `expect(mock).toHaveBeenCalledWith(...)` | Good — balanced with stubs |
| **Spy** (observe real behavior) | `vi.spyOn()` on real functions | Underused — could replace some `vi.mock()` |
| **Fake** (simplified implementation) | Signal-aware promise mocks | Good — used for AbortSignal tests |

### 4.4 Vitest Best Practices Compliance

| Practice | Status | Details |
|----------|--------|---------|
| Use `advanceTimersByTimeAsync` | Yes | All timer tests use async API |
| Restore timers in `afterEach` | Yes | Fixed anti-pattern globally |
| Restore mocks in `afterEach` | Yes | `vi.restoreAllMocks()` consistently |
| Avoid `as any` | Partial | Some casts remain for DI compatibility |
| Use `mockReset: true` in config | No | Manual reset in `afterEach` instead |
| Co-locate test files | No | Tests in `test/` directory tree |
| Use `it.each` for parameterized tests | Partial | Some tests could benefit |

---

## Part 5: Prioritized Improvement Recommendations

### Tier 1: High Impact, Low Effort

1. **Export proof-service utility functions** — Allow direct import in tests instead of replication
2. **Add `mockReset: true` to vitest.config.ts** — Auto-reset mock state between tests, reducing `afterEach` boilerplate
3. **Use `it.each()` for parameterized tests** — Convert repetitive test cases in `proof-service.spec.ts`, `date.spec.ts`

### Tier 2: Medium Impact, Medium Effort

4. **Add `createFixture()` integration tests for critical flows** (future phase):
   - Auth redirect flow
   - Loading sequence phases
   - Error boundary display
5. **Adopt POM pattern when adding Playwright E2E tests**
6. **Replace `vi.mock()` with `vi.spyOn()` in tests where import-time side effects are not a concern** (for new tests going forward)

### Tier 3: Low Impact, Quality of Life

7. **Remove `as any` casts** — Use `Partial<T>` more consistently
8. **Add test naming convention** — Prefer `"should [verb] when [condition]"` format
9. **Consider MSW (Mock Service Worker)** for future API-level integration tests

---

## Conclusion

The current test suite is **well-structured, reliable, and maintainable**. The DI-container-only approach is a deliberate, justified architectural decision that provides fast, deterministic tests for the Aurelia 2 framework.

Key strengths:
- Consistent patterns across 37 test files
- Proper timer and mock cleanup
- Comprehensive error scenario coverage
- Typed mock factories via centralized helpers

Key gaps (all acceptable trade-offs):
- No DOM rendering tests (mitigated by Storybook + future E2E)
- No POM abstraction (not needed at current scale)
- Heavy `vi.mock()` usage (justified by proto/auth import side effects)

The testing methodology aligns with modern best practices for **the unit test layer** of the testing trophy. The next evolution should focus on adding integration tests (`createFixture`) and E2E tests (Playwright) to complete the testing pyramid.
