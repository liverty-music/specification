## Context

The Aurelia 2 frontend has three components that bypass the framework's DI system to access browser APIs directly:

1. **`import-ticket-email-route.ts`** — reads `window.location.search` inside `loading()`, requiring tests to mutate `window.location` via `history.replaceState`.
2. **`event-detail-sheet.ts`** — calls `history.pushState`, `history.replaceState`, and `window.addEventListener('popstate')` directly; tests spy on the global `history` object.
3. **`dashboard-route.ts`** — calls `localStorage.getItem/setItem` via a static getter/setter and uses `this.element.closest('body')?.querySelectorAll('[data-nav]')` for DOM mutation; no unit tests exist.

The existing test pattern for (1) and (2) works (`vi.spyOn(history, 'pushState')`, `window.history.replaceState(…)`), but the DOM query in (3) requires constructing a real element tree with `[data-nav]` children, making `dashboard-route` untestable without a full DOM fixture. There is no `dashboard-route.spec.ts` today.

## Goals / Non-Goals

**Goals:**
- Make `dashboard-route.ts` fully unit-testable by eliminating the DOM query dependency and making `localStorage` access injectable.
- Align `import-ticket-email-route.ts` with Aurelia Router's `RouteNode.queryParams` API (the canonical way to read query parameters in `loading()`).
- Replace `window.addEventListener('popstate')` in `event-detail-sheet.ts` with Aurelia's `IRouterEvents` so the subscription is mockable via DI.
- Add `dashboard-route.spec.ts` covering the lane introduction state machine and key lifecycle paths.

**Non-Goals:**
- Refactoring the route component structure or decomposing routes into sub-controllers.
- Adding integration-level or E2E tests.
- Changing any observable component API (bindables, custom events, public methods).

## Decisions

### Decision 1: `INavDimmingService` for DOM mutation in `dashboard-route`

**Why:** `setNavTabsDimmed` traverses up to `<body>` and queries `[data-nav]` elements. This is a cross-cutting concern (nav tabs live in the shell, not the route). Injecting a service turns the DOM side-effect into an injectable call, making the route's state machine testable with a mock.

**Interface:**
```typescript
export interface INavDimmingService {
  setDimmed(dimmed: boolean): void
}
export const INavDimmingService = DI.createInterface<INavDimmingService>(
  'INavDimmingService', x => x.singleton(NavDimmingService)
)
```

**Implementation:** The concrete `NavDimmingService` uses `document.body.querySelectorAll('[data-nav]')` to find nav tab elements and sets a `data-dimmed` attribute (via `toggleAttribute`) rather than inline `style.setProperty`. Visual treatment (opacity, transition) is expressed in the `bottom-nav-bar.css` exception layer (`[data-nav][data-dimmed]`), keeping JS responsible only for state and CSS responsible for presentation. It is registered as a singleton in `main.ts`.

**Alternative considered:** Keep the DOM query in the route but accept it in tests by constructing a `document.body` fixture. Rejected because it makes tests order-dependent and brittle when shell structure changes.

---

### Decision 2: `ILocalStorage` for celebration/postSignup flags in `dashboard-route`

**Why:** `DashboardRoute.celebrationShown` and the `postSignupShown` check use `localStorage` directly via static getters and inline `localStorage.getItem` calls. Injecting an `ILocalStorage` wrapper makes these mockable with `Registration.instance(ILocalStorage, { getItem: vi.fn(), setItem: vi.fn(), removeItem: vi.fn() })`.

**Interface (minimal):**
```typescript
export interface ILocalStorage {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
  removeItem(key: string): void
}
export const ILocalStorage = DI.createInterface<ILocalStorage>(
  'ILocalStorage', x => x.instance(window.localStorage)
)
```

**Note:** `adapter/storage/` already provides typed storage helpers. `ILocalStorage` is a lower-level injectable that wraps the raw Web Storage API; the existing typed helpers remain unchanged.

**Alternative considered:** Use `vi.spyOn(localStorage, 'getItem')`. This works in jsdom but leaks state between tests and cannot be scoped per DI container. Rejected in favor of the explicit injection pattern already used elsewhere in the codebase.

---

### Decision 3: `IRouterEvents` subscription in `event-detail-sheet`

**Why:** The current `window.addEventListener('popstate', …)` handler replicates what Aurelia Router already tracks. Subscribing to `au:router:navigation-end` via `IRouterEvents` makes the subscription testable: tests inject a mock `IRouterEvents` and call the subscriber directly, with no `window.dispatchEvent(new PopStateEvent(…))` needed.

**Pattern:**
```typescript
export class EventDetailSheet implements IDisposable {
  private readonly routerEvents = resolve(IRouterEvents)
  private navSub: IDisposable | null = null

  public open(event: LiveEvent): void {
    this.event = event
    this.isOpen = true
    void this.router.load(`concerts/${event.id}`, { historyStrategy: 'push' })
    this.navSub = this.routerEvents.subscribe(
      'au:router:navigation-end', () => { if (this.isOpen) this.isOpen = false }
    )
  }

  public detaching(): void {
    this.navSub?.dispose()
  }
}
```

**Alternative considered:** Keep `vi.spyOn(history, 'pushState')` as the test strategy (it already works). The existing test suite passes with this approach. However, the direct `history` calls bypass the router lifecycle, meaning the URL is pushed outside the router's state, which can cause navigation inconsistencies on back/forward. Using `IRouter.load()` + `IRouterEvents` aligns with Aurelia idioms and is the canonical pattern per the framework docs.

**Trade-off:** Requires the route to have an Aurelia Router path for `/concerts/:id`. If none exists, `router.load()` will emit a navigation-error event. This is a pre-condition to verify before implementing.

---

### Decision 4: `RouteNode.queryParams` in `import-ticket-email-route`

**Why:** Aurelia Router passes `next: RouteNode` to `loading(params, next)`. `next.queryParams` is a `URLSearchParams` instance identical to what `new URLSearchParams(window.location.search)` would return, but it is derived from the router's internal navigation state rather than the live `window.location`. Tests can pass a fabricated `RouteNode`-like object without touching `window.location`.

**Signature change:**
```typescript
// Before
public async loading(): Promise<void> {
  const urlParams = new URLSearchParams(window.location.search)

// After
public async loading(_params: Params, next: RouteNode): Promise<void> {
  const urlParams = next.queryParams
```

**Test pattern:**
```typescript
const fakeNext = { queryParams: new URLSearchParams('title=T&text=チケット') }
await sut.loading({}, fakeNext as RouteNode)
```

No `window.history.replaceState` needed in tests.

---

## Risks / Trade-offs

- **`IRouterEvents` approach requires `/concerts/:id` route** → Verify `app-shell.ts` route config before implementing. If the route does not exist, fall back to keeping `history.pushState` (with the existing spy-based test strategy) as an interim solution.
- **`ILocalStorage` singleton uses `window.localStorage`** → In test environments (jsdom), `window.localStorage` is functional, so the default registration is safe. The DI override in tests replaces it with a mock.
- **`INavDimmingService` couples to shell DOM structure** → The concrete implementation still depends on `[data-nav]` attribute convention. If the shell is refactored, the service's querySelector must be updated. Documented in the service's JSDoc.

## Open Questions

~~Does `/concerts/:id` exist as a named Aurelia route in `app-shell.ts`?~~ **Resolved:** `path: 'concerts/:id'` is already configured in `app-shell.ts` (line 38). The `IRouter.load()` + `IRouterEvents` approach is safe to implement.
