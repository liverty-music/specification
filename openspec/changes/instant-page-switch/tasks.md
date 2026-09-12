## 1. Shared page-identity state

- [ ] 1.1 Create `src/services/page-header-state.ts` exposing `IPageHeaderState` via `DI.createInterface()`, registered `.singleton()`, with observable `titleKey`, `morphTitle`, and `activePath`, plus `setTitle(key, { morph })` and internal confirm/rollback helpers (last-confirmed snapshot).
- [ ] 1.2 Register `IPageHeaderState` in `main.ts` (or rely on the exported singleton token) so shell, nav, and routes resolve the same instance.
- [ ] 1.3 Unit-test the state transitions directly: optimistic set, confirm overrides optimistic, rollback restores last confirmed, `setTitle` updates title + morph.

## 2. Route title metadata

- [ ] 2.1 Add `titleKey` to each route's `data` in `app-shell.ts` for every route that shows a header (dashboard, discovery, my-artists, settings, and any other header route), matching the i18n key each route currently passes to `<page-header>`.
- [ ] 2.2 Add a resolver that maps an `au:router:navigation-start` target instruction to its route `data.titleKey` and its nav `activePath`.

## 3. Shell hosts the header and drives identity

- [ ] 3.1 In `app-shell.html`, render a single `<page-header title-key.bind="…" morph-title.bind="…">` bound to `IPageHeaderState`, placed in the shell grid `header` area, gated by `showNav` (same visibility as the nav bar).
- [ ] 3.2 In `app-shell.css`, change the grid to `grid-template-areas: "header" "viewport" "nav"` / `grid-template-rows: auto 1fr auto`; keep `<au-viewport>` unstyled; allow styling the shared `<page-header>` as a direct child.
- [ ] 3.3 In `app-shell.ts`, extend the router-event subscriptions: on `navigation-start` set the state optimistically from the target; on `navigation-end` reconcile from `ICurrentRoute` and record it as confirmed; on `navigation-error` roll back to the last confirmed snapshot. Keep the existing `showNav`/breadcrumb logic.
- [ ] 3.4 Unit-test the shell wiring with `test/helpers/mock-router-events`: assert state after start (optimistic), end (reconciled), and error (rolled back).

## 4. Bottom nav reads shared state

- [ ] 4.1 Repoint `bottom-nav-bar.ts` to read `IPageHeaderState.activePath` instead of `router.routeTree`; keep the sub-path highlight rules (`dashboard` also matches `concerts/…`).
- [ ] 4.2 Simplify `bottom-nav-bar.spec.ts` / fixture to inject state instead of mocking `routeTree`; assert `isActive` is a pure function of `activePath`.

## 5. Remove per-route headers

- [ ] 5.1 Remove `<page-header>` from `dashboard`, `discovery`, `my-artists`, `settings` (and any other) route templates; leave `page-help` and other siblings in place.
- [ ] 5.2 Remove the `"header"` area and its `auto` row from each route's `grid-template-areas` / `grid-template-rows`; verify content/controls still fill the viewport.
- [ ] 5.3 Change the dashboard mode toggle to call `IPageHeaderState.setTitle(modeTitleKey, { morph: true })` instead of binding a route-local title; confirm the title View-Transition morph still fires.

## 6. Stories, tests, and verification

- [ ] 6.1 Update/verify `page-header` and `bottom-nav-bar` Storybook stories for the new inputs (shell-bound title, `activePath`-driven highlight); keep a11y assertions passing.
- [ ] 6.2 Add an E2E assertion (functional project) that on a bottom-nav tap the active tab highlight and the header title switch before the incoming route's content settles (e.g. by delaying the route response).
- [ ] 6.3 Run `make check` (lint + unit) and the Playwright functional suite; confirm no route applies viewport-height/bottom-padding compensation and the shell grid renders header/viewport/nav correctly.
- [ ] 6.4 Manually verify in the browser (per project convention): tap each tab and confirm highlight + title change on the tap, ahead of content; confirm reduced-motion still switches instantly; confirm dashboard title morph.
