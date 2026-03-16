## 1. Dashboard route restructure

- [x] 1.1 Inline `live-highway` template into `dashboard-route.html` — replace `<live-highway>` with semantic HTML (`<header>`, `<main>`, `<ol>`, `<li>`, `<time>`)
- [x] 1.2 Move `onEventSelected` handler and `detailSheet` ref from `LiveHighway` into `DashboardRoute` TS
- [x] 1.3 Move `<event-detail-sheet>` element to `dashboard-route.html` as sibling of `<header>` and `<main>`
- [x] 1.4 Relocate `live-event.ts` type definitions (keep importable from `components/live-highway/` or move to `routes/dashboard/`)

## 2. Dashboard CSS rewrite

- [x] 2.1 Rewrite `dashboard-route.css`: define `dashboard-route` scope with `grid-template-columns: repeat(3, 1fr)` and `grid-template-rows: auto 1fr`
- [x] 2.2 Add `.stage-header` with `grid-column: 1 / -1` and `grid-template-columns: subgrid`
- [x] 2.3 Add `.concert-scroll` with `grid-column: 1 / -1`, `overflow-block: auto`, `min-block-size: 0`
- [x] 2.4 Add `.lane-grid` with `repeat(3, 1fr)`, `.lane` styles, and `[data-empty]` placeholder
- [x] 2.5 Migrate date-separator, stage-label, and lane typography styles from `live-highway.css`
- [x] 2.6 Preserve blur/needsRegion exception (`data-blurred`) on `<main>`
- [x] 2.7 Verify merged CSS stays within CUBE CSS ~80-line block limit

## 3. Delete live-highway component

- [x] 3.1 Delete `src/components/live-highway/live-highway.{ts,html,css}`
- [x] 3.2 Verify `event-card.{ts,html,css}` and `event-detail-sheet.{ts,html,css}` remain untouched and importable
- [x] 3.3 Update any remaining imports referencing `live-highway` (grep codebase)

## 4. Discovery route scroll fix

- [x] 4.1 Add height constraint to `discovery-route.css` height chain (ensure `.discover-layout` scroll container is properly constrained)
- [x] 4.2 Verify bottom-nav stays pinned on discovery with overflow content

## 5. E2E test updates

- [x] 5.1 Update `e2e/layout/dashboard.layout.spec.ts` selectors: `dashboard` → `dashboard-route`, `.highway-scroll` → `.concert-scroll`, `.highway-layout` → removed
- [x] 5.2 Increase mock concert data to 20 events across multiple dates (already done in stash)
- [x] 5.3 Add H4a test: assert `.concert-scroll` `scrollHeight > clientHeight` when content overflows
- [x] 5.4 Add H6 test: assert no element in height chain exceeds `au-viewport` height
- [x] 5.5 Update H4/H5 scroll tests to scroll 400px and verify header/footer positions
- [x] 5.6 Update `e2e/layout/discover.layout.spec.ts` for discovery route rename (`discover-page` → `discovery-route`)
- [x] 5.7 Run full `mobile-layout` test suite — all tests must pass

## 6. Validation

- [x] 6.1 Run `make check` (lint + test)
- [x] 6.2 Verify on local dev server with Pixel 7 emulation: scroll dashboard with 20+ concerts, confirm header/footer stay fixed
- [x] 6.3 Verify discovery page scroll behavior
