# Frontend Testing Strategy Guide

**Date**: 2026-02-25
**Repository**: `liverty-music/frontend`
**Framework**: Aurelia 2 + Vitest + Playwright

---

## 1. Current Test Patterns Assessment

### 1.1 What's Working Well

| Pattern | Where Used | Assessment |
|---------|-----------|------------|
| `createTestContainer()` helper | Newer tests (auth-status, event-card, etc.) | Excellent — clean DI setup with pre-registered logger |
| Typed mock factories | `test/helpers/mock-*.ts` | Good — `Partial<IInterface>` gives type safety |
| `vi.useFakeTimers()` for timer logic | my-artists-page, date converter | Correct approach for deterministic timer testing |
| Direct lifecycle hook invocation | auth-callback (`canLoad`), my-artists (`loading`) | Best practice for Aurelia 2 route testing |
| `INode` injection for CustomEvent testing | event-card | Correct Aurelia 2 pattern for host element events |
| `vi.mock()` + dynamic import for side-effectful modules | my-artists-page | Correct Vitest hoisting pattern |
| Fresh DI container per test (`beforeEach`) | All tests | Ensures test isolation |

### 1.2 Issues Found

#### Issue 1: `vi.useRealTimers()` inside `it()` blocks (HIGH)

**File**: `test/routes/my-artists-page.spec.ts`

```
Problem:
  vi.useRealTimers() is called inside it() blocks instead of afterEach().
  If a test throws before reaching this line, fake timers leak into subsequent tests.

Fix:
  Move to afterEach(() => { vi.useRealTimers() })
```

#### Issue 2: `any` type for mock objects (MEDIUM)

**File**: `test/auth-service.spec.ts`

```
Problem:
  let userManagerMock: any
  Defeats TypeScript's contract checking. Mock shape can silently diverge from real interface.

Fix:
  Use Partial<UserManager> or a typed factory like createMockUserManager().
```

#### Issue 3: Inline logger mock duplicating helper (LOW)

**File**: `test/auth-service.spec.ts`

```
Problem:
  Manually creates { scopeTo: vi.fn().mockReturnThis(), debug: vi.fn(), ... }
  instead of using createTestContainer() which already handles this.

Fix:
  Migrate to createTestContainer() pattern (already used in newer tests).
```

#### Issue 4: `@ts-expect-error` for private member access (MEDIUM)

**File**: `test/auth-service.spec.ts`

```
Problem:
  // @ts-expect-error - access private for test
  sut.user = { expired: false }
  Fragile against refactors. Tests break silently when private fields are renamed.

Fix:
  Test through public API or expose a test-only setter via DI configuration.
  Alternative: use vi.spyOn(sut as any, 'user', 'get').mockReturnValue(...)
```

#### Issue 5: Skipped DOM rendering tests (TECH DEBT)

**File**: `test/my-app.spec.ts`

```
Problem:
  it.skip('should render the landing page message', ...)
  it.skip('should have a layout with navigation and viewport', ...)
  Dead code with stale test bodies.

Fix:
  Either implement using createFixture (see Section 3) or remove the skipped blocks
  and track as a GitHub issue.
```

#### Issue 6: `setup.ts` fixture cleanup is dead code

```
Problem:
  onFixtureCreated() callback + fixtures array + afterEach cleanup is never triggered
  because no test uses createFixture().

Assessment:
  Not harmful — it's infrastructure for future use.
  Keep it, but document that it's waiting for createFixture adoption.
```

---

## 2. Testing Architecture: Recommended Approach per Module Type

### 2.1 Testing Trophy for This Project

```
         ▲
        / \
       /E2E \        ← Playwright: 4-6 critical user journeys
      /───────\
     /Component\     ← createFixture: template bindings, DOM interactions
    /───────────\
   /  DI Unit    \   ← DI container: services, route guards, component logic
  /───────────────\
 /   Pure Unit     \  ← No DI: utilities, value converters, pure functions
/───────────────────\
│  Static Analysis  │  ← TypeScript strict + Biome lint
└───────────────────┘
```

### 2.2 Decision Matrix: Which Test Type for Each Module

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST TYPE DECISION FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Is it a pure function with no dependencies?                           │
│  ├── YES → Pure Unit Test (no DI, no DOM)                              │
│  │         Examples: artistColor(), bytesToDecimal(), DateValueConverter│
│  │                                                                      │
│  └── NO → Does it have DI dependencies?                                │
│           ├── YES → Does the test need to verify DOM output?           │
│           │         ├── YES → Component Integration Test (createFixture)│
│           │         │         Examples: template bindings, if.bind,     │
│           │         │                   repeat.for, click handlers      │
│           │         │                                                   │
│           │         └── NO → DI Unit Test (createTestContainer)        │
│           │                  Examples: service methods, canLoad guards, │
│           │                           computed properties, event dispatch│
│           │                                                             │
│           └── NO → Is it a cross-cutting user journey?                 │
│                    └── YES → E2E Test (Playwright)                     │
│                              Examples: onboarding flow, auth redirect  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Mapping: Every Module Type → Recommended Test Approach

| Module Type | Test Approach | DI? | DOM? | Key Technique |
|---|---|---|---|---|
| Pure utility functions | Pure Unit | No | No | Direct function call |
| Value converters | Pure Unit | No | No | `new Converter().toView(...)` |
| Services (gRPC wrappers) | DI Unit | Yes | No | Mock RPC client via `Registration.instance` |
| Services (complex logic) | DI Unit | Yes | No | Mock deps + `vi.useFakeTimers()` + AbortController |
| Route guards (`canLoad`) | DI Unit | Yes | No | Direct method invocation, assert return value |
| Route data loading (`loading`) | DI Unit | Yes | No | Mock services, assert state mutations |
| Component computed properties | DI Unit | Yes | No | `container.get(Component)` → read property |
| Component CustomEvent dispatch | DI Unit | Yes | Minimal | `INode` mock + `addEventListener` |
| Component template bindings | Component Integration | Yes | Yes | `createFixture` + `assertText` / `getBy` |
| Component DOM interactions | Component Integration | Yes | Yes | `createFixture` + DOM event dispatch |
| Auth hook (`@lifecycleHooks`) | DI Unit | Yes | No | Direct `canLoad(params, routeNode)` |
| ConnectRPC interceptors | DI Unit | Partial | No | Mock `next` function, fake timers |
| Full user journeys | E2E | N/A | N/A | Playwright POM |

---

## 3. Detailed Test Patterns by Category

### 3.1 Pure Unit Tests

**Target**: Pure functions, value converters, utility modules

**Pattern**: Direct invocation, no DI container, no DOM

```
Applicable files:
  ✅ Already tested: artistColor(), DateValueConverter
  ❌ Needs tests:    bytesToDecimal(), uuidToFieldElement(), bytesToHex() (proof-service.ts)
                     sanitize() (error-boundary-service.ts)
                     mintDate(), formatTokenId() (tickets-page.ts)
```

**Best practices**:
- Use table-driven tests (`it.each`) for input/output pairs
- No `beforeEach` needed — each test is self-contained
- No mocking required
- These are the cheapest tests to write and maintain

**Example structure**:
```
describe('bytesToDecimal', () => {
  it.each([
    { input: new Uint8Array([0]),    expected: '0' },
    { input: new Uint8Array([1]),    expected: '1' },
    { input: new Uint8Array([0xff]), expected: '255' },
    { input: new Uint8Array([1, 0]), expected: '256' },
  ])('converts $input to $expected', ({ input, expected }) => {
    expect(bytesToDecimal(input)).toBe(expected)
  })
})
```

---

### 3.2 DI Unit Tests (Services)

**Target**: Services with injected dependencies

**Pattern**: `createTestContainer()` + mock registrations

```
Applicable files:
  ✅ Already tested: DashboardService, AuthService
  ❌ Needs tests:    ArtistDiscoveryService, LoadingSequenceService,
                     ConcertService, ErrorBoundaryService, ConnectErrorRouter,
                     EntryService, TicketService, ProofService,
                     NotificationManager, PushService
```

**Best practices**:
- One mock factory per service interface in `test/helpers/`
- Use `Partial<IService>` for type-safe mocks
- Test error paths explicitly (rejected promises, AbortError)
- For timer-dependent services: `vi.useFakeTimers()` in `beforeEach`, `vi.useRealTimers()` in `afterEach`

**Service complexity tiers**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Tier 1: Thin gRPC wrappers (ConcertService, EntryService, etc.)   │
│ ──────────────────────────────────────────────────────────────────  │
│ Pattern: Mock the ConnectRPC client, verify call forwarding        │
│ Focus:   AbortSignal propagation, error forwarding                 │
│ Mocks:   1 (the RPC client)                                       │
│ Effort:  Low                                                       │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 2: Stateful services (ErrorBoundaryService, NotifManager)     │
│ ──────────────────────────────────────────────────────────────────  │
│ Pattern: Verify state mutations through public API                 │
│ Focus:   Observable state changes, ring buffer limits, sanitize    │
│ Mocks:   0-1 (mostly self-contained)                               │
│ Effort:  Medium                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 3: Orchestrators (LoadingSequenceService, ArtistDiscovery)    │
│ ──────────────────────────────────────────────────────────────────  │
│ Pattern: Mock all deps + fake timers + AbortController             │
│ Focus:   Batch parallelism, retry/rollback, timeout, min delay     │
│ Mocks:   2-4 services                                              │
│ Effort:  High                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 4: Interceptors (ConnectErrorRouter, grpc-transport)          │
│ ──────────────────────────────────────────────────────────────────  │
│ Pattern: Mock `next` function, inject error codes                  │
│ Focus:   Error classification, retry backoff, auth refresh         │
│ Mocks:   next function + auth service                              │
│ Effort:  Medium-High                                               │
└─────────────────────────────────────────────────────────────────────┘
```

**Interceptor testing pattern** (for connect-error-router.ts):

```
Structure:
  describe('createAuthRetryInterceptor', () => {
    // Create interceptor with mock auth
    // Create mock `next` function that returns ConnectRPC UnaryResponse
    // For error cases: mock `next` to throw ConnectError with specific Code

    it('retries with fresh token on Unauthenticated error')
      // 1st call: next throws ConnectError(Code.Unauthenticated)
      // Verify: signinSilent() called
      // 2nd call: next succeeds
      // Verify: response returned

    it('redirects to /welcome when token refresh fails')
      // next throws Unauthenticated
      // signinSilent throws
      // Verify: window.location.href === '/welcome'

    it('passes through non-auth errors')
      // next throws ConnectError(Code.NotFound)
      // Verify: error re-thrown without interception
  })
```

**AbortController testing pattern** (for loading-sequence-service.ts):

```
Structure:
  describe('aggregateData', () => {
    it('aborts all in-flight requests after global timeout')
      // vi.useFakeTimers()
      // Start aggregateData (no await yet)
      // vi.advanceTimersByTime(10_000)  // GLOBAL_TIMEOUT_MS
      // await vi.runAllTimersAsync()
      // Verify: result.status === 'partial' or 'failed'
      // Verify: abort signal was triggered

    it('waits minimum display time even if data loads fast')
      // Mock services to resolve immediately
      // Start aggregateData
      // vi.advanceTimersByTime(2999)  // just under MINIMUM_DISPLAY_MS
      // Verify: promise still pending
      // vi.advanceTimersByTime(1)
      // await result
      // Verify: result.status === 'complete'
  })
```

---

### 3.3 DI Unit Tests (Route Components)

**Target**: Route lifecycle hooks and component logic

**Pattern**: `createTestContainer()` + test lifecycle hooks as plain async methods

```
Applicable files:
  ✅ Already tested: AuthCallback, MyArtistsPage
  ❌ Needs tests:    Dashboard, DiscoverPage, ArtistDiscoveryPage,
                     LoadingSequence, TicketsPage, SettingsPage
```

**Best practices**:
- Test `canLoad` → return value (true / false / redirect path string)
- Test `loading` → state mutations on the component instance
- Test `detaching` → cleanup (abort controllers, timers)
- For routes with `AbortController`: verify abort on `detaching`
- For routes with stale-data logic: verify old data preserved on reload failure

**Route guard testing pattern** (for auth-hook.ts):

```
Structure:
  describe('AuthHook', () => {
    describe('canLoad', () => {
      it('allows public routes (data.auth === false) without auth check')
        // routeNode.data = { auth: false }
        // Don't even set up auth mock
        // Verify: returns true

      it('allows authenticated users on protected routes')
        // mockAuth.isAuthenticated = true
        // Verify: returns true

      it('redirects unauthenticated users to /welcome')
        // mockAuth.isAuthenticated = false
        // Verify: returns '/welcome' (or equivalent redirect)
        // Verify: toast.show() called

      it('awaits authService.ready before checking authentication')
        // mockAuth.ready = new Promise that doesn't resolve yet
        // Start canLoad (no await)
        // Verify: result is still pending
        // Resolve the ready promise
        // Verify: now resolves
    })
  })
```

**Dashboard stale-data pattern**:

```
Structure:
  describe('Dashboard', () => {
    describe('loadData', () => {
      it('shows fresh data on successful load')

      it('preserves old data and marks as stale on reload failure')
        // 1st load: succeed with data A
        // 2nd load: fail with error
        // Verify: sut.groupedEvents still contains data A
        // Verify: sut.isStale === true

      it('ignores AbortError (navigation-triggered)')
        // Mock service to throw DOMException('AbortError')
        // Verify: sut.error is NOT set
    })
  })
```

---

### 3.4 Component Integration Tests (createFixture)

**Target**: Template bindings, conditional rendering, DOM event handling

**Pattern**: `@aurelia/testing` `createFixture` with dependency injection

```
Candidates for createFixture (template logic that cannot be tested via DI alone):
  - bottom-nav-bar: if.bind active tab highlighting
  - error-banner: template conditional rendering (error visible/hidden)
  - notification-prompt: conditional display based on permission + dismissal
  - region-setup-sheet: dialog open/close, quick-city buttons, dropdown
  - event-detail-sheet: touch drag-to-dismiss (DOM events)
```

**When to use createFixture vs DI-only**:

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   CAN YOU TEST IT BY READING/WRITING COMPONENT PROPERTIES?          │
│                                                                      │
│   YES ──────────────────────► DI Unit Test (preferred, faster)      │
│   │                                                                  │
│   │  Examples:                                                       │
│   │  • sut.isActive('dashboard') → true                             │
│   │  • sut.googleMapsUrl → 'https://...'                            │
│   │  • await sut.loading(); expect(sut.events).toHaveLength(3)      │
│   │                                                                  │
│   NO ───────────────────────► createFixture Integration Test        │
│                                                                      │
│   Examples:                                                          │
│   • "When error is null, the banner element is not in DOM"          │
│   • "The repeat.for renders 47 prefecture options"                  │
│   • "Clicking a quick-city button selects the mapped prefecture"    │
│   • "Touch drag > 100px closes the sheet"                           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**createFixture pattern**:

```
Structure:
  describe('RegionSetupSheet (integration)', () => {
    it('renders 47 prefectures in the dropdown')
      // const { getBy, getAllBy } = await createFixture(
      //   '<region-setup-sheet></region-setup-sheet>',
      //   {},
      //   [RegionSetupSheet, Registration.instance(ILogger, createMockLogger())]
      // ).started
      //
      // const options = getAllBy('option')
      // expect(options).toHaveLength(47 + 1)  // +1 for placeholder

    it('renders 6 quick-city buttons')
      // const { getAllBy } = await createFixture(...)
      // const buttons = getAllBy('[data-testid="quick-city"]')
      // expect(buttons).toHaveLength(6)
  })
```

**Important**: Most component tests in this project should remain DI-only. Use `createFixture` sparingly for cases where the template logic itself is complex or buggy.

---

### 3.5 E2E Tests (Playwright)

**Target**: Critical user journeys across multiple pages

**Pattern**: Page Object Model (POM)

```
Recommended E2E scenarios (4-6 tests):
  1. Onboarding flow:   /welcome → auth → /artist-discovery → /loading → /dashboard
  2. Auth redirect:     Unauthenticated visit to /dashboard → /welcome
  3. Dashboard browse:  /dashboard → tap event → detail sheet → Google Maps link
  4. Settings:          /settings → change region → /dashboard reloads
  5. Ticket entry:      /tickets → generate QR code → modal displays
  6. Discover artists:  /discover → search → follow → bubble appears
```

**Page Object Model structure**:

```
e2e/
  pages/
    welcome.page.ts
    artist-discovery.page.ts
    dashboard.page.ts
    settings.page.ts
    tickets.page.ts
  fixtures/
    auth.fixture.ts          ← reusable auth setup (storageState)
  tests/
    onboarding.spec.ts
    auth-redirect.spec.ts
    dashboard-browse.spec.ts
    settings.spec.ts
```

**POM best practices**:
- Each page class encapsulates locators and actions
- Tests read like user stories: `await dashboard.openEventDetail(0)`
- Use `data-testid` attributes for stable selectors (not CSS classes)
- Keep E2E tests few but high-value (cover critical paths only)
- Use Playwright's `storageState` for authenticated test sessions (already configured in `playwright.config.mjs`)

**POM example structure**:

```
class DashboardPage {
  constructor(private page: Page) {}

  // Locators
  readonly eventCards = () => this.page.locator('[data-testid="event-card"]')
  readonly regionLabel = () => this.page.locator('[data-testid="region-label"]')
  readonly retryButton = () => this.page.locator('[data-testid="retry-button"]')

  // Actions
  async openEventDetail(index: number) {
    await this.eventCards().nth(index).click()
  }

  async waitForLoaded() {
    await this.eventCards().first().waitFor({ state: 'visible' })
  }
}
```

---

## 4. Mock Helper Improvements

### 4.1 Current mock helpers vs recommended additions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MOCK HELPER INVENTORY                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  EXISTING (test/helpers/):                                          │
│  ✅ createTestContainer()        ← DI container factory            │
│  ✅ createMockLogger()           ← ILogger                         │
│  ✅ createMockAuth()             ← IAuthService                    │
│  ✅ createMockConcertService()   ← IConcertService                 │
│  ✅ createMockArtistServiceClient() ← IArtistServiceClient         │
│  ✅ createMockArtistDiscoveryService() ← IArtistDiscoveryService   │
│                                                                     │
│  RECOMMENDED ADDITIONS:                                             │
│  ❌ createMockToastService()     ← IToastService                   │
│  ❌ createMockRouter()           ← IRouter                         │
│  ❌ createMockErrorBoundary()    ← IErrorBoundaryService           │
│  ❌ createMockTicketService()    ← ITicketService                  │
│  ❌ createMockProofService()     ← IProofService                   │
│  ❌ createMockPushService()      ← IPushService                    │
│  ❌ createMockNotificationMgr()  ← INotificationManager            │
│  ❌ createMockLoadingSequence()  ← ILoadingSequenceService         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Mock factory best practices

**Rules for mock factories**:
1. Return `Partial<IInterface>` for type safety
2. All methods default to `vi.fn()` with sensible defaults (resolve empty, return null)
3. Accept an optional config object for common overrides
4. Keep in `test/helpers/mock-*.ts` (one file per service or grouped by domain)

**Pattern**:

```
// test/helpers/mock-router.ts
export function createMockRouter(): Partial<IRouter> {
  return {
    load: vi.fn().mockResolvedValue(undefined),
  }
}
```

---

## 5. Addressing Specific Technical Challenges

### 5.1 Module-level side effects (`vi.mock` + dynamic import)

**Problem**: Some modules create instances at parse time (e.g., `new UserManager()` in auth-service.ts, RPC client instantiation).

**Solution** (already used in my-artists-page.spec.ts):

```
Step 1: Create a local DI interface stub
  const mockIRouter = DI.createInterface('IRouter')

Step 2: vi.mock the module BEFORE any import
  vi.mock('@aurelia/router', () => ({ IRouter: mockIRouter }))

Step 3: Dynamic import the SUT AFTER mocks
  const { MyComponent } = await import('../../src/routes/my-component')

Step 4: Register the SUT and resolve
  container.register(MyComponent)
  sut = container.get(MyComponent)
```

**Files that need this pattern**:
- Any module importing from `@aurelia/router` (`IRouter`)
- Any module importing `auth-service.ts` (has module-level `window.location`)
- Any module importing proto-generated RPC clients

### 5.2 Browser API mocking

| API | Mock Strategy |
|-----|--------------|
| `localStorage` | Already available via JSDOM (setup.ts) — use `localStorage.clear()` in `afterEach` |
| `window.location.href` (assignment) | `Object.defineProperty(window, 'location', { value: { href: '' }, writable: true })` |
| `window.open` | `vi.spyOn(window, 'open').mockImplementation(() => null)` |
| `navigator.clipboard.writeText` | `Object.assign(navigator, { clipboard: { writeText: vi.fn() } })` |
| `Notification.permission` | `Object.defineProperty(Notification, 'permission', { value: 'default', configurable: true })` |
| `navigator.serviceWorker` | `Object.defineProperty(navigator, 'serviceWorker', { value: { ready: Promise.resolve(mockReg) } })` |
| `crypto.subtle.digest` | `vi.spyOn(crypto.subtle, 'digest').mockResolvedValue(...)` |
| `Worker` constructor | `vi.stubGlobal('Worker', MockWorkerClass)` |
| `requestAnimationFrame` | `vi.spyOn(global, 'requestAnimationFrame').mockImplementation(cb => { cb(0); return 0 })` |
| `HTMLDialogElement.showModal/close` | Attach mock methods to the element: `el.showModal = vi.fn()` |
| `history.pushState/replaceState` | `vi.spyOn(history, 'pushState')` |
| `fetch` | `vi.stubGlobal('fetch', vi.fn().mockResolvedValue(...))` or MSW |
| `TouchEvent` | Construct manually: `new TouchEvent('touchstart', { touches: [{ clientY: 100 }] })` or use a factory helper |

### 5.3 Timer management rules

```
RULES:
  1. vi.useFakeTimers()   → ALWAYS in beforeEach (never inside it())
  2. vi.useRealTimers()   → ALWAYS in afterEach  (never inside it())
  3. vi.advanceTimersByTime(ms) → for setTimeout/setInterval
  4. await vi.runAllTimersAsync() → AFTER advanceTimersByTime, if timers trigger promises
  5. vi.setSystemTime(date)     → for Date.now() / new Date() dependent code
  6. vi.restoreAllMocks()       → ALWAYS in afterEach
```

### 5.4 AbortController testing pattern

```
Pattern for testing cancellable operations:

  // Test: external abort cancels the operation
  const controller = new AbortController()
  const promise = sut.doWork(controller.signal)
  controller.abort()

  // Depending on expected behavior:
  await expect(promise).rejects.toThrow('AbortError')  // if it throws
  // OR
  const result = await promise
  expect(result.status).toBe('aborted')                // if it handles gracefully

  // Test: verify nested calls receive the signal
  expect(mockService.fetchData).toHaveBeenCalledWith(
    expect.objectContaining({ signal: expect.any(AbortSignal) })
  )
```

---

## 6. Recommended Test File Naming and Structure

### 6.1 Directory structure (mirrors src/)

```
test/
  setup.ts
  helpers/
    create-container.ts
    mock-auth.ts
    mock-logger.ts
    mock-rpc-clients.ts
    mock-router.ts                    ← NEW
    mock-error-boundary.ts            ← NEW
    mock-toast.ts                     ← NEW
    mock-notification.ts              ← NEW
    browser-mocks.ts                  ← NEW (shared browser API mocking utilities)
  components/
    area-selector-sheet.spec.ts       ← existing
    auth-status.spec.ts               ← existing
    bottom-nav-bar.spec.ts            ← NEW
    error-banner.spec.ts              ← NEW
    notification-prompt.spec.ts       ← NEW
    region-setup-sheet.spec.ts        ← NEW
    live-highway/
      color-generator.spec.ts         ← existing
      event-card.spec.ts              ← existing
      event-detail-sheet.spec.ts      ← NEW
      live-highway.spec.ts            ← existing
  hooks/
    auth-hook.spec.ts                 ← NEW
  routes/
    auth-callback.spec.ts             ← existing
    dashboard.spec.ts                 ← NEW
    my-artists-page.spec.ts           ← existing
    discover-page.spec.ts             ← NEW
    artist-discovery-page.spec.ts     ← NEW
    loading-sequence.spec.ts          ← NEW
    settings-page.spec.ts             ← NEW
    tickets-page.spec.ts              ← NEW
  services/
    artist-discovery-service.spec.ts  ← NEW
    concert-service.spec.ts           ← NEW
    connect-error-router.spec.ts      ← NEW
    dashboard-service.spec.ts         ← existing
    entry-service.spec.ts             ← NEW
    error-boundary-service.spec.ts    ← NEW
    grpc-transport.spec.ts            ← NEW
    loading-sequence-service.spec.ts  ← NEW
    notification-manager.spec.ts      ← NEW
    proof-service.spec.ts             ← NEW
    push-service.spec.ts              ← NEW
    ticket-service.spec.ts            ← NEW
    toast-notification.spec.ts        ← existing
  value-converters/
    date.spec.ts                      ← existing
  my-app.spec.ts                      ← existing

e2e/
  pages/                              ← NEW: Page Object Model
    welcome.page.ts
    artist-discovery.page.ts
    dashboard.page.ts
    settings.page.ts
    tickets.page.ts
  fixtures/
    auth.fixture.ts
  tests/
    onboarding.spec.ts
    auth-redirect.spec.ts
    dashboard-browse.spec.ts
```

### 6.2 Test file template (standard)

```
describe('[ModuleName]', () => {
  let sut: ModuleName

  beforeEach(() => {
    // 1. Create mocks
    // 2. Build DI container
    // 3. Resolve SUT
  })

  afterEach(() => {
    vi.restoreAllMocks()
    // Clean up: localStorage.clear(), vi.useRealTimers(), etc.
  })

  describe('[methodName]', () => {
    it('should [expected behavior] when [condition]', async () => {
      // Arrange
      // Act
      // Assert
    })
  })
})
```

---

## 7. Coverage Threshold Roadmap

### Current thresholds

```
statements: 20%  |  branches: 70%  |  functions: 30%  |  lines: 20%
```

### Recommended progression

| Phase | Statements | Branches | Functions | Lines | Milestone |
|-------|-----------|----------|-----------|-------|-----------|
| Current | 20% | 70% | 30% | 20% | 12 test files |
| Phase 1 | 40% | 70% | 45% | 40% | +Priority 1 tests (auth-hook, loading-sequence, connect-error-router, etc.) |
| Phase 2 | 55% | 75% | 55% | 55% | +Priority 2 tests (routes, remaining services) |
| Phase 3 | 65% | 80% | 65% | 65% | +Priority 3 tests (components, settings) |
| Target | 70% | 80% | 70% | 70% | Stable maintenance level |

### Coverage exclusion review

```
Current exclusions that should STAY excluded:
  ✅ src/main.ts                    ← app bootstrap, not testable
  ✅ src/components/dna-orb/**      ← canvas, requires special setup
  ✅ src/**/*.stories.ts            ← Storybook files
  ✅ *.config.*                     ← config files
  ✅ scripts/**                     ← build scripts

Current exclusion that should be RECONSIDERED:
  ⚠️  src/services/auth-service.ts  ← has tests but excluded due to window.location
      → Fix: refactor module-level window.location access to a lazy getter
      → Then remove from exclusion list

Current exclusion that should be RECONSIDERED:
  ⚠️  src/*-page.ts                 ← "env teardown issues"
      → Investigate if createFixture teardown in setup.ts fixes this
      → If not, document the specific teardown issue
```

---

## 8. Anti-Pattern Checklist

Use this checklist when reviewing or writing tests:

| Anti-Pattern | Fix |
|---|---|
| `any` type for mocks | Use `Partial<IInterface>` or typed factory |
| `vi.useRealTimers()` inside `it()` | Move to `afterEach()` |
| `@ts-expect-error` for private access | Test through public API or use `vi.spyOn` |
| Inline mock objects duplicating helpers | Use shared factory from `test/helpers/` |
| `it.skip` with stale test body | Implement or remove (track in issue) |
| Testing implementation details | Test observable outputs (return values, state changes, mock calls) |
| Asserting on internal state | Assert on public properties or method return values |
| Missing `vi.restoreAllMocks()` in afterEach | Always include in afterEach |
| Missing `localStorage.clear()` for tests using localStorage | Include in afterEach |
| Shared mutable state between tests | Rebuild everything in `beforeEach` |

---

## 9. Summary: Key Decisions

| Decision | Recommendation | Rationale |
|---|---|---|
| Primary test approach | DI Unit (createTestContainer) | Already proven in codebase, covers 80% of needs |
| When to use createFixture | Template binding verification only | Most logic is testable without DOM |
| Mock strategy | Typed factories in test/helpers/ | Type safety + reusability |
| Timer testing | vi.useFakeTimers in beforeEach, vi.useRealTimers in afterEach | Prevents timer leaks |
| E2E approach | Playwright POM, 4-6 critical journeys | Infrastructure already configured |
| Coverage target | 70% statements / 80% branches | Achievable with Priority 1-3 tests |
| Module-level side effects | vi.mock + dynamic import | Already established pattern |
| Browser API mocking | vi.spyOn / Object.defineProperty / vi.stubGlobal | Per-API strategy (see Section 5.2) |
