## Context

The Discover page uses a CSS Grid layout (`auto auto auto 1fr`) with a full-viewport canvas inside the last row. The canvas component (`dna-orb-canvas`) uses Shadow DOM with `position: absolute; inset: 0` to fill its container. However, the containing block chain is broken — `.bubble-area` lacks `position: relative`, so the canvas resolves to `.discover-layout` (which has `position: relative` for its starfield `::before` pseudo-element), covering the entire page including the search bar and genre chips.

Current CSS architecture:
```
.discover-layout  (position: relative) ← unintended containing block
├── ::before      (position: absolute; inset: 0) ← starfield overlay
├── .search-bar
├── .genre-chips
├── .onboarding-hud
└── .bubble-area  (position: static) ← should be containing block
    └── dna-orb-canvas → canvas (position: absolute; inset: 0)
```

## Goals / Non-Goals

**Goals:**
- Fix the containing block chain so canvas renders only within `.bubble-area`
- Use `container-type: size` on `.bubble-area` for proper container query support
- ~~Eliminate `position: relative` from `.discover-layout`~~ (reverted — grid stacking breaks auto-placement; containing block fixed via `.bubble-area` instead)
- Migrate state toggling (browse/search modes) to `data-state` attributes per CUBE CSS exception pattern
- Replace the `.orb-label` magic number (`inset-block-end: 10rem`) with container-relative units

**Non-Goals:**
- Refactoring the Matter.js physics engine or orb rendering logic
- Changing the Shadow DOM CSS inside `dna-orb-canvas` (the fix is upstream)
- Redesigning the search results layout
- Changing the app shell grid (`my-app.css`)

## Decisions

### 1. ~~Grid single-cell stacking for starfield `::before`~~ → Keep `position: absolute` overlay

**Decision:** Keep `position: relative` on `.discover-layout` and `position: absolute; inset: 0` on the starfield `::before`. Fix the containing block chain by adding `position: relative` to `.bubble-area` instead.

**Rationale:** Grid single-cell stacking was attempted (`grid-row: 1 / -1; grid-column: 1 / -1` on `::before`) but reverted because placing the pseudo-element into an explicit grid cell broke CSS Grid auto-placement — content children were pushed to implicit columns, destroying the layout. The simpler fix is to establish `.bubble-area` as its own containing block so the canvas resolves there, while keeping the existing `position: absolute` overlay pattern for the starfield.

**Original approach (reverted):** Replace `position: absolute` on `::before` with Grid single-cell stacking to eliminate `position: relative` from `.discover-layout`. This broke auto-placement of grid children.

**Current approach:** The containing block issue is fully resolved by `position: relative` on `.bubble-area` + `overflow: hidden` + `container-type: size`. The canvas now correctly resolves to `.bubble-area` regardless of `.discover-layout` also being positioned.

### 2. `container-type: size` on `.bubble-area`

**Decision:** Use `container-type: size` (both axes) instead of `container-type: inline-size`.

**Rationale:** The bubble area needs both-axis containment for container-relative positioning of the orb label (`cqb` units). Since `.bubble-area` receives its block size from the Grid `1fr` row (externally determined), the `size` containment requirement (explicit sizing on both axes) is satisfied.

**Alternative considered:** Keep `inline-size` and use percentage-based positioning for the orb label. This works but misses the opportunity to use container queries for responsive adjustments to the orb size and label placement.

### 3. `data-state` attribute for browse/search mode

**Decision:** Add `data-state="search"` on `.discover-layout` and use CSS attribute selectors for visibility toggling.

**Rationale:** CUBE CSS methodology requires state deviations to use `data-*` attributes, not CSS classes. This also centralizes the state on the parent rather than toggling `.hidden` on each child independently.

**Implementation:**
```html
<div class="discover-layout" data-state.bind="isSearchMode ? 'search' : null">
```
```css
.discover-layout[data-state="search"] .bubble-area { display: none; }
.discover-layout:not([data-state="search"]) .search-results { display: none; }
```

### 4. Container-relative orb label positioning

**Decision:** Replace `inset-block-end: 10rem` with `inset-block-end: 15cqb` (15% of container block size).

**Rationale:** The current `10rem` is a magic number that doesn't adapt to different container sizes. Using `cqb` units ties the label position to the actual bubble area height, keeping the orb label proportionally positioned regardless of viewport size.

## Risks / Trade-offs

- **`container-type: size` requires external sizing** → Mitigated: `.bubble-area` is in a Grid `1fr` row, so block-size is always determined by the grid. If the grid structure changes in the future, this containment may need revisiting.
- **`position: relative` retained on `.discover-layout`** → Originally planned to remove, but grid stacking broke auto-placement. The containing block issue is fully mitigated by `.bubble-area` having its own `position: relative` + `overflow: hidden`, so the canvas resolves to `.bubble-area` not `.discover-layout`.
- **`cqb` unit browser support** → Container query units are Baseline Widely Available (2023+). No concern for the target audience (modern mobile browsers).
- **`data-state` migration** → Minimal risk. Only affects the template binding expression and CSS selectors. No JS logic change needed beyond the binding.
