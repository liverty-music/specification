## 1. New Injectable Services

- [x] 1.1 Create `src/services/nav-dimming-service.ts` — define `INavDimmingService` interface with `setDimmed(dimmed: boolean): void`, implement `NavDimmingService` using `document.body.querySelectorAll('[data-nav]')`, register as singleton with `DI.createInterface`
- [x] 1.2 Create `src/adapter/storage/local-storage.ts` — define `ILocalStorage` interface (`getItem`, `setItem`, `removeItem`), register default instance as `window.localStorage` via `DI.createInterface` with `x.instance(window.localStorage)`
- [x] 1.3 Register `INavDimmingService` in `src/main.ts`

## 2. Refactor: dashboard-route.ts

- [x] 2.1 Inject `INavDimmingService` and replace all `setNavTabsDimmed()` DOM query calls with `this.navDimming.setDimmed(dimmed)`
- [x] 2.2 Inject `ILocalStorage` and replace the static `celebrationShown` getter/setter (which calls `localStorage` directly) with instance calls through `ILocalStorage`
- [x] 2.3 Replace the inline `localStorage.getItem(StorageKeys.postSignupShown)` call in `attached()` with `ILocalStorage.getItem(…)`
- [x] 2.4 Remove the `private static get/set celebrationShown` accessors (now handled via `ILocalStorage`)

## 3. Refactor: import-ticket-email-route.ts

- [x] 3.1 Change `loading()` signature to `loading(_params: Params, next: RouteNode): Promise<void>`
- [x] 3.2 Replace `new URLSearchParams(window.location.search)` with `next.queryParams`
- [x] 3.3 Update `import-ticket-email-route.spec.ts` — remove all `window.history.replaceState(…)` setup calls; pass `{ queryParams: new URLSearchParams('…') }` as second argument to `loading()`

## 4. Refactor: event-detail-sheet.ts

- [x] 4.1 Inject `IRouter` (from `@aurelia/router`) and `IRouterEvents`
- [x] 4.2 In `open()`, replace `history.pushState(…)` with `void this.router.load(\`concerts/${event.id}\`, { historyStrategy: 'push' })`
- [x] 4.3 Replace `window.addEventListener('popstate', this.onPopstate)` with `this.navSub = this.routerEvents.subscribe('au:router:navigation-end', …)` that closes the sheet when `isOpen` is true and the navigation is not to `/concerts/:id`
- [x] 4.4 In `close()` and `onSheetClosed()`, replace `history.replaceState(null, '', '/dashboard')` with `void this.router.load('dashboard', { historyStrategy: 'replace' })`
- [x] 4.5 In `detaching()`, replace `window.removeEventListener` with `this.navSub?.dispose()`
- [x] 4.6 Update `event-detail-sheet.spec.ts` — replace `vi.spyOn(history, 'pushState')` with mock `IRouter.load` spy; replace `vi.spyOn(history, 'replaceState')` with assertions on `mockRouter.load`; inject mock `IRouterEvents` with a `subscribe` spy

## 5. New Test Helpers

- [x] 5.1 Create `test/helpers/mock-nav-dimming-service.ts` — export `createMockNavDimmingService()` returning `{ setDimmed: vi.fn() }`
- [x] 5.2 Create `test/helpers/mock-local-storage.ts` — export `createMockLocalStorage(initial?: Record<string, string>)` that returns an in-memory `ILocalStorage` implementation with `getItem`, `setItem`, `removeItem` as Vitest spies
- [x] 5.3 Create `test/helpers/mock-router-events.ts` — export `createMockRouterEvents()` returning `{ subscribe: vi.fn().mockReturnValue({ dispose: vi.fn() }) }`

## 6. New Test: dashboard-route.spec.ts

- [x] 6.1 Create `test/routes/dashboard-route.spec.ts` with `vi.mock` stubs for all 8 service imports (auth, concert, follow, journey, onboarding, guest, user, i18n) plus `INavDimmingService` and `ILocalStorage`
- [x] 6.2 Write `describe('loading')` — authenticated user with/without home sets `needsRegion`; unauthenticated completed-onboarding user sets `showSignupBanner`
- [x] 6.3 Write `describe('attached')` — DASHBOARD onboarding step triggers lane intro; `postSignupShown === 'pending'` sets `showPostSignupDialog`
- [x] 6.4 Write `describe('lane intro state machine')` — `startLaneIntro` → home phase; `onLaneIntroTap` advances through home→near→away→done; `completeLaneIntro` shows celebration when not yet shown; `completeLaneIntro` undims nav when already shown
- [x] 6.5 Write `describe('onCelebrationDismissed')` — sets `showCelebration = false`, calls `setDimmed(false)`, calls `deactivateSpotlight()`
- [x] 6.6 Write `describe('detaching')` — aborts controller, calls `setDimmed(false)`
- [x] 6.7 Write `describe('@watch onDateGroupsChanged')` — when `dateGroups.length` transitions from 0 to >0 during `'home'` phase in onboarding, `updateSpotlightForPhase` is called (via `queueTask` + `vi.advanceTimersByTime`)

## 7. Coverage Threshold Update

- [x] 7.1 Update `vitest.config.ts` coverage thresholds: statements → 70%, branches → 78%, functions → 70%, lines → 70%

## 8. Verification

- [x] 8.1 Run `make lint` — no Biome or TypeScript errors
- [x] 8.2 Run `make test` — all unit tests pass, coverage thresholds met
