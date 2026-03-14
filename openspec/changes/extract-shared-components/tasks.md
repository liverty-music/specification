# Tasks: extract-shared-components

## 1. Create `<svg-icon>` component

- [ ] 1.1 Create `src/components/svg-icon/svg-icon.ts` — custom element with `name` and `size` bindable props
- [ ] 1.2 Create `src/components/svg-icon/svg-icon.html` — template with switch/case for icon names
- [ ] 1.3 Create `src/components/svg-icon/svg-icon.css` — size variants (sm/md/lg)
- [ ] 1.4 Register in `main.ts`
- [ ] 1.5 Define icon set: home, discover, tickets, settings, my-artists, check, alert-triangle, info, x-circle, music, search, chevron-right, trash, map-pin, calendar, link, arrow-left
- [ ] 1.6 Write unit tests for svg-icon

## 2. Refactor to use `<svg-icon>`

- [ ] 2.1 bottom-nav-bar.html: replace 5 inline SVG switch/case blocks with `<svg-icon>`
- [ ] 2.2 toast-notification.html: replace 3 severity icon SVGs with `<svg-icon>`
- [ ] 2.3 tickets-page.html: replace inline SVGs with `<svg-icon>`
- [ ] 2.4 my-artists-page.html: replace inline SVGs with `<svg-icon>`
- [ ] 2.5 dashboard.html: replace inline SVGs with `<svg-icon>`
- [ ] 2.6 discover-page.html: replace search icon SVG with `<svg-icon>`
- [ ] 2.7 settings-page.html: replace inline SVGs with `<svg-icon>`
- [ ] 2.8 event-detail-sheet.html: replace detail row icons with `<svg-icon>`

## 3. Create `<state-placeholder>` component

- [ ] 3.1 Create `src/components/state-placeholder/state-placeholder.ts` — bindable props: icon, title, description, ctaLabel
- [ ] 3.2 Create `src/components/state-placeholder/state-placeholder.html` — icon + title + description + optional CTA slot
- [ ] 3.3 Create `src/components/state-placeholder/state-placeholder.css` — centered layout with design tokens
- [ ] 3.4 Register in `main.ts`
- [ ] 3.5 Write unit tests for state-placeholder

## 4. Refactor to use `<state-placeholder>`

- [ ] 4.1 tickets-page.html: replace empty state and error state blocks
- [ ] 4.2 my-artists-page.html: replace empty state block
- [ ] 4.3 dashboard.html: replace error state block
- [ ] 4.4 discover-page.html: replace empty search results block (if applicable)

## 5. Create `<page-shell>` component

- [ ] 5.1 Create `src/components/page-shell/page-shell.ts` — bindable props: titleKey, showHeader
- [ ] 5.2 Create `src/components/page-shell/page-shell.html` — `<main>` + `<header>` + `<au-slot name="header-actions">` + `<au-slot>` (default content)
- [ ] 5.3 Create `src/components/page-shell/page-shell.css` — shared page layout styles
- [ ] 5.4 Register in `main.ts`
- [ ] 5.5 Write unit tests for page-shell

## 6. Refactor to use `<page-shell>`

- [ ] 6.1 tickets-page.html: wrap in `<page-shell>`
- [ ] 6.2 my-artists-page.html: wrap in `<page-shell>`
- [ ] 6.3 dashboard.html: wrap in `<page-shell>`
- [ ] 6.4 settings-page.html: wrap in `<page-shell>`
- [ ] 6.5 discover-page.html: wrap in `<page-shell>`
- [ ] 6.6 Remove duplicated page layout CSS from individual route stylesheets

## 7. Update tests

- [ ] 7.1 Update existing tests for refactored pages (DOM selector changes)
- [ ] 7.2 Update E2E layout assertions if affected

## 8. Verification

- [ ] 8.1 `make lint` passes
- [ ] 8.2 `make test` passes
- [ ] 8.3 No duplicated SVG definitions remain in templates (grep check)
- [ ] 8.4 No `.state-center` > `.state-content` pattern remains (grep check)
- [ ] 8.5 All route pages use `<page-shell>` wrapper
