## Why

Dashboard and discovery pages have a broken height-constraint chain: the `live-highway` component's scroll container expands to fit its content instead of being constrained by the viewport, causing headers and the bottom-nav to scroll off-screen on mobile when concert data overflows. The previous fix (PR #202) addressed CSS but did not resolve the root cause — a 6-layer height chain with unconstrained intermediate elements. Additionally, the `live-highway` component is a thin wrapper (18 lines of TS) that duplicates state management already handled by the dashboard's `promise.bind`, adding unnecessary DOM depth.

## What Changes

- **Eliminate `live-highway` component**: Inline its template and styles into `dashboard-route`, removing 3 files and reducing the height chain from 6 layers to 2.
- **Restructure dashboard DOM with semantic HTML**: Replace `<div>` soup with `<header>`, `<main>`, `<ol>`, `<li>`, `<time>`, `<section>` elements. Reduce div count from 11+ to 0.
- **Adopt CSS subgrid for column alignment**: Dashboard root defines `repeat(3, 1fr)` columns; `.stage-header` inherits via `subgrid` for guaranteed column sync.
- **Fix scroll containment**: Establish a 2-layer height chain (`dashboard-route` → `<main .concert-scroll>`) with `overflow-block: auto` only on the scroll container.
- **Use CSS `:empty` for empty lanes**: Replace conditional template markup (`if.bind` + dash placeholder) with CSS `:empty::after`.
- **Consolidate CSS into single block file**: Merge `live-highway.css` styles into `dashboard-route.css`, keeping it within the CUBE CSS ~80-line block limit.
- **Update E2E layout tests**: Increase mock concert count to overflow viewport; add height-chain validation and scroll-container constraint assertions.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `shell-layout`: Height-constraint chain behavior changes — dashboard route must constrain all descendants to viewport height, with only the concert scroll area being scrollable.

## Impact

- **Frontend files changed**: `src/routes/dashboard/dashboard-route.{html,css,ts}`, `src/routes/discovery/discovery-route.{html,css}`
- **Frontend files deleted**: `src/components/live-highway/live-highway.{html,css,ts}` (event-card and event-detail-sheet remain)
- **Frontend files moved**: `src/components/live-highway/live-event.ts` → re-export or move to `src/routes/dashboard/`
- **E2E tests updated**: `e2e/layout/dashboard.layout.spec.ts`, `e2e/layout/discover.layout.spec.ts` (selectors, mock data, new assertions)
- **No backend or API changes**
- **No breaking changes to other routes** — only dashboard and discovery are affected
