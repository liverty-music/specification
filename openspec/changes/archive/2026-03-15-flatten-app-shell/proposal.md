## Why

The current frontend layout has excessive DOM nesting — 8 layers from app-shell to scrollable content on the dashboard. Every route wraps its content in a `<page-shell>` component that adds a custom element boundary + `<main>` + optional header, creating a fragile height chain where `block-size: 100%` must resolve correctly through 5+ custom element boundaries. This chain breaks because CSS Grid's `1fr` (= `minmax(auto, 1fr)`) allows tracks to expand beyond the container's `100dvh`, causing sticky headers to scroll away and `overflow-y: auto` to have no effect. Additionally, the DOM uses non-semantic `<div>` elements throughout where landmark and sectioning elements should be used.

## What Changes

- **BREAKING**: Remove `page-shell` component — each route defines its own `<header>` + `<main>` directly as top-level children
- Rename `my-app` to `app-shell` — the root component provides only `<au-viewport>` + `<bottom-nav-bar>` + top-layer overlays
- Flatten route DOM structures — eliminate intermediate wrapper divs (`.app-viewport`, `.dashboard-body`, `.dashboard-promise-slot`)
- Fix Grid track sizing — change `1fr` to `minmax(0, 1fr)` at both `app-shell` and `au-viewport` levels to prevent content-driven track expansion
- Replace non-semantic `<div>` elements with appropriate HTML landmark/sectioning elements (`<header>`, `<main>`, `<section>`, `<ul>`, `<article>`, `<search>`, `<aside>`) following web.dev and MDN structural best practices

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-shell-layout`: Grid structure changes from 2-row to 2-row with `minmax(0, 1fr)`. Remove `page-shell` delegation — routes own their `<header>` and `<main>`. Remove `<main>` from app-shell level (routes provide it). Remove `.app-viewport` wrapper div.
- `shell-layout`: Overlay exclusion rules remain but apply to the simplified DOM structure. Stage header stickiness is achieved via route-level grid layout rather than nested component hierarchy.

## Impact

- **Frontend routes**: All route templates must be updated to remove `page-shell` and provide `<header>` + `<main>` directly
- **page-shell component**: Deleted entirely (HTML, CSS, TS files)
- **my-app → app-shell**: Rename across all references (component registration, route config, CSS, tests)
- **CSS**: Route-specific CSS must be updated — selectors scoped to `page-shell` or `.page-layout` need migration to route-level scoping
- **Accessibility**: Landmark structure improves — screen readers gain proper `banner`, `main`, `navigation` landmarks per page
- **Tests**: Unit tests referencing `page-shell` or `my-app` need updates
