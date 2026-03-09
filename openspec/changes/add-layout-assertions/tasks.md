## 1. Infrastructure setup

- [x] 1.1 Add a `mobile` project to `playwright.config.mjs` with `devices['iPhone 14']` viewport (390×844) and `baseURL: 'http://localhost:9000'`.
- [x] 1.2 Create `e2e/layout/` directory and a shared RPC mock helper (`e2e/layout/fixtures.ts`) that intercepts Connect-RPC requests via `page.route()` and returns minimal valid responses.
- [x] 1.3 Create a shared layout assertion helper (`e2e/layout/assertions.ts`) with reusable functions: `expectFillsViewport(locator)`, `expectContainedIn(child, parent)`, `expectAnchored(locator, edge, value)`.

## 2. Shell layout assertions

- [x] 2.1 Create `e2e/layout/shell.layout.spec.ts`: verify `my-app` height equals viewport height (S1).
- [x] 2.2 Assert `au-viewport` height + `bottom-nav-bar` height equals `my-app` height on a route with nav (S2).
- [x] 2.3 Assert `bottom-nav-bar` bottom edge equals viewport height (S3).
- [x] 2.4 Assert `au-viewport` fills full `my-app` height on a route without nav — use `/welcome` (S4).

## 3. Discover page assertions

- [x] 3.1 Create `e2e/layout/discover.layout.spec.ts`: verify `.discover-layout` fills viewport width and `au-viewport` height (D1).
- [x] 3.2 Assert `.bubble-area` width equals `.discover-layout` width (D2 — prevents right-edge clipping).
- [x] 3.3 Assert canvas element fills `.bubble-area` (width and height within 1px tolerance) after canvas initialization (D3).
- [x] 3.4 Assert `.search-bar` right edge does not exceed viewport width (D4).
- [x] 3.5 Assert `.bubble-area` bottom does not exceed `bottom-nav-bar` top (D5).

## 4. Loading sequence assertions

Removed: The loading-sequence page is fundamentally transient (navigates away immediately after `loading()` resolves). Reliably holding it visible in E2E is not practical without coupling tests to internal Aurelia router mechanics.

## 5. Authenticated route assertions (consolidated from simplify-shell-layout)

- [x] 5.1 Add an `authenticated-mobile` project to `playwright.config.mjs` with `devices['iPhone 14']` viewport, `baseURL`, and `storageState` for test user auth.
- [x] 5.2 Create `e2e/layout/settings.auth.spec.ts`: verify settings page content fills height, has overflow-y auto, and is contained within viewport using real auth (test user).

## 6. Integration and verification

- [x] 6.1 Integrate layout tests into `make check` pipeline (add `test-layout` and `test-layout-auth` targets to Makefile).
- [x] 6.2 Run the full layout test suite (`mobile-layout` project) and verify all assertions pass.
- [x] 6.3 Run `make check` to confirm lint + unit tests + layout tests all pass together.
