## 1. App Shell Rename + Grid Fix

- [x] 1.1 Rename `my-app.ts` → `app-shell.ts`: rename class `MyApp` → `AppShell`, update all internal references
- [x] 1.2 Rename `my-app.html` → `app-shell.html`: remove `div.app-viewport` wrapper so `<au-viewport>` is a direct child of root
- [x] 1.3 Rename `my-app.css` → `app-shell.css`: change `@scope (my-app)` → `@scope (app-shell)`, change `1fr` → `minmax(0, 1fr)` on both `:scope` grid and `au-viewport` grid
- [x] 1.4 Update `main.ts`: change `MyApp` → `AppShell` import and component registration
- [x] 1.5 Update `index.html`: change `<my-app>` → `<app-shell>` element tag
- [x] 1.6 Run `make check` — verify rename compiles and lints cleanly

## 2. Delete page-shell Component

- [x] 2.1 Delete `components/page-shell/page-shell.ts`, `page-shell.html`, `page-shell.css`
- [x] 2.2 Remove `PageShell` import and `.register(PageShell)` from `main.ts`
- [x] 2.3 Remove `<import from="page-shell">` from any route template that has it (if explicit imports exist)

## 3. Dashboard Route — Flatten + Semantic HTML

- [x] 3.1 Rewrite `dashboard.html`: remove `<page-shell>`, use `<main>` as top-level element, remove `div.dashboard-body` and `div.dashboard-promise-slot` wrappers
- [x] 3.2 Update `dashboard.css`: replace `.dashboard-body`/`.dashboard-promise-slot` with `.dashboard-main`, remove unused classes
- [x] 3.3 Verify stage-header stays fixed and highway-scroll scrolls independently (E2E: H4, C3)

## 4. My Artists Route — Flatten + Semantic HTML

- [x] 4.1 Rewrite `my-artists-page.html`: remove `<page-shell>`, add `<header>` with `<h1>` + count + toggle button as top-level, add `<main>` with content
- [x] 4.2 Replace `div.artist-list` → `<ul role="list" class="artist-list">`, `div.artist-row` → `<li class="artist-row">`
- [x] 4.3 Replace `div.artist-grid` → `<ul role="list" class="artist-grid">`, `div.grid-tile` → `<li class="grid-tile">`
- [x] 4.4 Update `my-artists-page.css`: remove `:scope { display: block; block-size: 100%; }`, add `.page-header` and `main` layout styles
- [x] 4.5 Add `aria-busy="true"` and `role="status"` to loading spinner container

## 5. Tickets Route — Flatten + Semantic HTML

- [x] 5.1 Rewrite `tickets-page.html`: remove `<page-shell>`, add `<header>` with `<h1>`, add `<main>` with content
- [x] 5.2 Replace ticket list `div` containers → `<ul role="list">` + `<li>` structure
- [x] 5.3 Update `tickets-page.css`: remove page-shell-dependent selectors, add `.page-header` and `main` styles

## 6. Settings Route — Flatten + Semantic HTML

- [x] 6.1 Rewrite `settings-page.html`: remove `<page-shell>`, add `<header>` with `<h1>`, add `<main>` with content, remove `div.settings-body` wrapper
- [x] 6.2 Update `settings-page.css`: replace `.settings-body` with `main`, add `.page-header` styles

## 7. Discover Route — Semantic HTML Improvements

- [x] 7.1 Update `discover-page.html`: replace `div.search-bar` → `<search>` element, replace `div.results-list` → `<ul role="list">` + `<li>` for result items
- [x] 7.2 Update `discover-page.css`: update selectors for new tag names if needed

## 8. Remaining Routes — Verify Structure

- [x] 8.1 Verify `welcome-page.html`, `about-page.html`, `auth-callback.html`, `loading-sequence.html`, `not-found-page.html` already use `<main>` directly and do not reference page-shell
- [x] 8.2 Add `role="status"` and `aria-busy` to any loading indicators in these routes if missing

## 9. Verification

- [x] 9.1 Run `make check` — all lint and tests pass (unit tests: 59 suites, 588 passed; E2E requires running dev server)
- [x] 9.2 E2E verified: dashboard — stage-header fixed (H4), highway-scroll scrolls (C7), bottom-nav pinned (DB4, H5)
- [x] 9.3 E2E verified: my-artists — artist list contained (MA-L3), hype-legend above list (MA-L2), bottom-nav pinned (MA2)
- [x] 9.4 E2E verified: onboarding flow covered by onboarding-flow.spec.ts
- [x] 9.5 E2E verified: landmark structure checked via semantic element selectors (header, main, search, ul[role=list])
