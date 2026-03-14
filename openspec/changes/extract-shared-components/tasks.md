# Tasks: extract-shared-components

## 1. Create `<svg-icon>` component

- [x] 1.1 Create `src/components/svg-icon/svg-icon.ts` — custom element with `name` and `size` bindable props
- [x] 1.2 Create `src/components/svg-icon/svg-icon.html` — template with switch/case for icon names
- [x] 1.3 Create `src/components/svg-icon/svg-icon.css` — size variants (sm/md/lg)
- [x] 1.4 Register in `main.ts`
- [x] 1.5 Define icon set: home, discover, tickets, settings, my-artists, check, alert-triangle, info, x-circle, music, search, chevron-right, trash, map-pin, calendar, link, arrow-left
- [x] 1.6 Write unit tests for svg-icon

## 2. Refactor to use `<svg-icon>`

- [x] 2.1 bottom-nav-bar.html: replace 5 inline SVG switch/case blocks with `<svg-icon>`
- [x] 2.2 toast-notification.html: replace 3 severity icon SVGs with `<svg-icon>`
- [x] 2.3 tickets-page.html: replace inline SVGs with `<svg-icon>`
- [x] 2.4 my-artists-page.html: replace inline SVGs with `<svg-icon>`
- [x] 2.5 dashboard.html: replace inline SVGs with `<svg-icon>`
- [x] 2.6 discover-page.html: replace search icon SVG with `<svg-icon>`
- [x] 2.7 settings-page.html: replace inline SVGs with `<svg-icon>`
- [x] 2.8 event-detail-sheet.html: replace detail row icons with `<svg-icon>`

## 3. Create `<state-placeholder>` component

- [x] 3.1 Create `src/components/state-placeholder/state-placeholder.ts` — bindable props: icon, title, description, ctaLabel
- [x] 3.2 Create `src/components/state-placeholder/state-placeholder.html` — icon + title + description + optional CTA slot
- [x] 3.3 Create `src/components/state-placeholder/state-placeholder.css` — centered layout with design tokens
- [x] 3.4 Register in `main.ts`
- [x] 3.5 Write unit tests for state-placeholder

## 4. Refactor to use `<state-placeholder>`

- [x] 4.1 tickets-page.html: replace empty state and error state blocks
- [x] 4.2 my-artists-page.html: replace empty state block
- [x] 4.3 dashboard.html: replace error state block
- [x] 4.4 discover-page.html: skip — empty search results use a simple `search-status` div with `t` attribute, not the `.state-center` pattern

## 5. Create `<page-shell>` component

- [x] 5.1 Create `src/components/page-shell/page-shell.ts` — bindable props: titleKey, showHeader
- [x] 5.2 Create `src/components/page-shell/page-shell.html` — `<main>` + `<header>` + `<au-slot name="header-actions">` + `<au-slot>` (default content)
- [x] 5.3 Create `src/components/page-shell/page-shell.css` — shared page layout styles
- [x] 5.4 Register in `main.ts`
- [x] 5.5 Write unit tests for page-shell

## 6. Refactor to use `<page-shell>`

- [x] 6.1 tickets-page.html: wrap in `<page-shell>`
- [x] 6.2 my-artists-page.html: wrap in `<page-shell>`
- [x] 6.3 dashboard.html: wrap in `<page-shell>`
- [x] 6.4 settings-page.html: wrap in `<page-shell>`
- [x] 6.5 discover-page.html: skip — uses `data-search-mode.bind` on `<main>` for CSS state changes; wrapping in page-shell would lose this binding
- [x] 6.6 Remove duplicated page layout CSS from individual route stylesheets

## 7. Update tests

- [x] 7.1 Update existing tests for refactored pages (DOM selector changes)
- [x] 7.2 Update E2E layout assertions if affected

## 8. Verification

- [x] 8.1 `make lint` passes
- [x] 8.2 `make test` passes (556 passed, 2 skipped)
- [x] 8.3 No duplicated SVG definitions remain in route templates (grep check: 0 matches)
- [x] 8.4 `.state-center` in route CSS is only used for loading spinners, not duplicated empty-state patterns
- [x] 8.5 All applicable route pages use `<page-shell>` (4/4); discover-page intentionally skipped
