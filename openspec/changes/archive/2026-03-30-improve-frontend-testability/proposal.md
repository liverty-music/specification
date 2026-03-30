## Why

Several Aurelia 2 frontend components access browser APIs (`window.location`, `history`, `localStorage`, DOM `querySelectorAll`) directly, making unit tests require real browser state and fragile setup. This blocks high-confidence testing of critical flows like the Dashboard lane introduction and deep-link sheet behavior. Aligning these components with Aurelia Router's lifecycle hooks and DI patterns removes the browser-API coupling and enables pure unit tests.

## What Changes

- **`import-ticket-email-route.ts`**: Replace `window.location.search` with `next.queryParams` from the Aurelia Router `loading(params, next: RouteNode)` hook signature, eliminating `window.location` dependency in tests.
- **`event-detail-sheet.ts`**: Replace direct `history.pushState` / `window.addEventListener('popstate')` with `IRouterEvents` subscriptions and `IRouter.load()` for navigation, making history interaction injectable and mockable.
- **`dashboard-route.ts`**: Extract `setNavTabsDimmed` DOM-query logic into a dedicated injectable `INavDimmingService`, and move `localStorage` access for celebration/postSignup flags into the existing `adapter/storage` pattern with an injectable `ILocalStorage` abstraction. Add `dashboard-route.spec.ts` covering the lane introduction state machine and key lifecycle scenarios.

## Capabilities

### New Capabilities

- `frontend-router-query-params`: Using Aurelia Router's `RouteNode.queryParams` API instead of `window.location.search` in route lifecycle hooks.

### Modified Capabilities

- `frontend-testing`: Add `dashboard-route` test scenarios covering the lane introduction state machine, `loading()`, `attached()`, and `detaching()` hooks. Raise coverage thresholds to reflect new route tests.
- `dashboard-lane-introduction`: The `setNavTabsDimmed` behavior is now delegated to an injectable service rather than direct DOM queries; observable contract remains the same.

## Impact

- `frontend/src/routes/import-ticket-email/import-ticket-email-route.ts` — signature change on `loading()`
- `frontend/src/routes/dashboard/dashboard-route.ts` — inject `INavDimmingService`; inject `ILocalStorage` for celebration/postSignup flags
- `frontend/src/components/live-highway/event-detail-sheet.ts` — inject `IRouterEvents` + `IRouter`; remove `window` calls
- `frontend/src/services/nav-dimming-service.ts` — new file
- `frontend/src/adapter/storage/local-storage.ts` — new DI-injectable wrapper (or augment existing `adapter/storage`)
- `frontend/test/routes/dashboard-route.spec.ts` — new file
- `frontend/test/helpers/` — new mock factories for `INavDimmingService`, `ILocalStorage`, `IRouterEvents`
- No API or protobuf changes; frontend-only refactor
