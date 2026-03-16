## Context

The dashboard route renders concert events in a 3-lane layout (HOME / NEAR / AWAY stages). The current implementation delegates rendering to a `live-highway` custom element, which creates a deep DOM/CSS height chain that fails to constrain `overflow-block: auto` — the scroll container expands to content height instead of being constrained by the viewport. This causes headers and the bottom-nav-bar to scroll off-screen on mobile.

Current height chain (6 layers):
```
au-viewport → dashboard-route → .dashboard-main → live-highway → .highway-layout → .highway-scroll
```

The `live-highway` component is a thin wrapper (18 lines TS, 2 bindables) whose state management duplicates what `dashboard-route` already handles via `promise.bind`.

## Goals / Non-Goals

**Goals:**
- Fix the scroll overflow bug so stage-header and bottom-nav remain fixed during scrolling
- Eliminate `live-highway` as a separate component, inlining into `dashboard-route`
- Adopt semantic HTML (`<header>`, `<main>`, `<ol>`, `<li>`, `<time>`) — zero `<div>` elements
- Use CSS subgrid chain from root grid through all intermediate elements to guarantee column alignment
- Use CSS `:empty` pseudo-class to replace template-level empty lane conditionals
- Keep `dashboard-route.css` within CUBE CSS ~80-line block limit
- Update E2E tests to detect the scroll overflow regression with realistic data volumes

**Non-Goals:**
- Refactoring `event-card` or `event-detail-sheet` components (they remain independent)
- Changing the discovery route's internal layout (only fixing the same scroll bug there)
- Adding new features or changing business logic
- Responsive breakpoint changes

## Decisions

### D1: Inline `live-highway` into `dashboard-route`

**Choice:** Remove `live-highway` CE; move its template and styles directly into `dashboard-route`.

**Why:** `live-highway` adds a DOM layer that breaks the height chain. Its TS logic is trivial — `isEmpty` (derivable inline) and `onEventSelected` (move to `dashboard-route`). The `promise.bind` in `dashboard-route` already manages loading/error/success states, making `live-highway`'s internal loading/empty states redundant.

**Alternative considered:** Keep `live-highway` but fix its CSS height chain. Rejected because it preserves unnecessary complexity and the component provides no meaningful encapsulation.

### D2: Dashboard root as 3-column grid with named areas and full subgrid chain

**Choice:** `dashboard-route` `:scope` defines a 3-column grid using the `grid-template` shorthand with named areas:
```css
grid-template:
  "stage-home stage-near stage-away" auto
  "lane-home  lane-near  lane-away" minmax(0, 1fr)
  / 1fr 1fr 1fr;
```
Named areas create implicit line names (e.g., `stage-home-start`, `stage-away-end`) enabling self-documenting `grid-column` assignments like `grid-column: stage-home / stage-away`. All intermediate elements use `grid-template-columns: subgrid` to propagate the 3-column layout:

`:scope` → `.stage-header` → `.concert-scroll` → `.date-group-list` → `li` → `.lane-grid` → `.lane` (auto-placed)

**Why:** A single `grid-template` definition is the source of truth for column layout. Subgrid propagation ensures every level inherits exact column tracks — no duplicate column definitions that can drift out of sync. Named areas make the grid visually readable and self-documenting.

**Note:** `repeat()` is invalid inside the `grid-template` shorthand (`<explicit-track-list>` syntax). Must use `1fr 1fr 1fr` instead of `repeat(3, 1fr)`.

**Alternative considered:** Keep independent `repeat(3, 1fr)` on both header and lane-grid. Simpler, but misses the opportunity to use modern CSS and risks column misalignment if one changes without the other.

### D3: `<main .concert-scroll>` as the sole scroll container with subgrid

**Choice:** The `<main>` element gets `grid-column: lane-home / lane-away; grid-template-columns: subgrid; overflow-block: auto; min-block-size: 0`. This is the only element in the chain that scrolls. It participates in the subgrid chain, propagating the 3-column layout to all descendants. Additionally, `app-shell.css` was updated to use `grid-template-rows: minmax(0, 1fr) auto` (changed from `1fr auto`) to constrain `au-viewport` at the outer level.

**Why:** CSS `1fr` defaults to `minmax(auto, 1fr)`, where the `auto` minimum allows the grid track to expand to content height, breaking overflow containment. Both levels of the height chain — `app-shell` (outer) and `dashboard-route` (inner) — require `minmax(0, 1fr)` to force a zero minimum and enable `overflow-block: auto` on the scroll container. The height chain is: `app-shell (minmax(0,1fr))` → `au-viewport` → `dashboard-route (auto minmax(0,1fr))` → `<main .concert-scroll>`. This fix also benefits all other routes (discovery, my-artists) since the outer constraint applies globally.

Subgrid on `.concert-scroll` is essential — without it, the scroll container would break the subgrid chain and descendant elements could not inherit the root grid's column tracks. Each intermediate element (`.date-group-list`, `li`, `.lane-grid`) uses `grid-column: 1 / -1; grid-template-columns: subgrid` to continue the chain.

### D4: Semantic HTML — `<ol>` + `<li>` for date groups and lanes

**Choice:**
- Date groups: `<ol .date-group-list>` → `<li>` per group (ordered by date)
- Lanes within a group: `<ol .lane-grid>` → `<li .lane>` per stage
- Date labels: `<time>` instead of `<span>`
- Empty lanes: CSS `:empty::after` pseudo-element instead of conditional `<div>` + `<p>`

**Why:** Improves accessibility tree, reduces template conditionals, follows web-design-specialist semantic element requirements.

### D5: `event-detail-sheet` moves to `dashboard-route` template

**Choice:** Place `<event-detail-sheet>` as a sibling of `<header>` and `<main>` in `dashboard-route.html`. Wire `event-selected` event via bubbling on `<main>`.

**Why:** It's a dialog/popover (top-layer) — DOM position is irrelevant to rendering. Moving it out of a deleted component is necessary.

### D6: Discovery route — minimal scroll fix only

**Choice:** Apply the same overflow fix pattern to `discovery-route` but do NOT restructure its DOM. Only add `block-size: 100%` and `min-block-size: 0` to the height chain where missing.

**Why:** Discovery's layout is different (search bar + genre chips + bubble area, not a concert list). A full restructure is out of scope.

## Risks / Trade-offs

**[Subgrid browser support]** → Subgrid is Baseline 2023. All target browsers support it. No fallback needed.

**[`:empty` with Aurelia `repeat.for`]** → When `repeat.for` renders 0 items, Aurelia leaves comment nodes inside the element, which means `:empty` may not match. → Mitigation: Verify in E2E test; if `:empty` doesn't work with Aurelia comments, fall back to `[data-empty]` attribute set via binding.

**[CSS file size after merge]** → Merging `live-highway.css` into `dashboard-route.css` could exceed CUBE CSS's ~80-line block limit. → Mitigation: Event-card styles remain in their own file. Date-separator and lane-grid styles are compact. The merged block should stay within limits since loading/empty states in `live-highway.css` are replaced by `promise.bind` states.

**[E2E test selectors]** → Route rename (`dashboard` → `dashboard-route`) changed CE tag names. Existing tests using `querySelector('dashboard')` will break. → Mitigation: Update all selectors as part of E2E test task.
