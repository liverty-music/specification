## Why

The frontend CSS relies almost entirely on flexbox for page-level layouts (12 flex contexts vs 1 grid context). CSS Grid with subgrid and Container Queries are already listed as platform standards in the `modern-css-platform` spec, but adoption is minimal — Container Queries appear in only 2 files, grid only in the app shell, and subgrid is unused. Migrating to grid/subgrid eliminates `flex-shrink: 0` hacks, enables explicit row/column tracks, and pairs naturally with Container Queries for component-level responsive design.

## What Changes

- Convert `.discover-layout` from `flex-direction: column` to CSS Grid with explicit row tracks (`auto auto 1fr`), replacing `flex-shrink: 0` / `flex: 1` patterns.
- Convert `.results-list` + `.result-item` to CSS Grid with subgrid so avatar and name columns align across all items without nested flex calculations.
- Convert `.loading-layout` from flex centering to `display: grid; place-items: center`.
- Add `container-type: inline-size` to `.search-results` and `.bubble-area` so child components can use `@container` rules instead of depending on viewport width.
- Update `.onboarding-hud` and `.progress-dots` from flex to grid for consistent gap/alignment.

## Capabilities

### New Capabilities

_None — this change implements existing requirements from `modern-css-platform` and `app-shell-layout`._

### Modified Capabilities

- `modern-css-platform`: Expanding Container Queries requirement with scenarios for discover page search results and bubble area containers.
- `discover`: Layout implementation shifts from flexbox to CSS Grid/subgrid.

## Impact

- **CSS files**: `discover-page.css`, `loading-sequence.css` (primary), `my-app.css` (minor container-type additions)
- **Layout tests**: Existing Playwright layout assertions in `e2e/layout/` validate structural relationships (bounding boxes, containment). These tests should continue to pass after migration — they verify outcomes, not implementation approach.
- **No JS changes**: Pure CSS refactor with no TypeScript or HTML template modifications.
- **No API changes**: Frontend-only, no backend impact.
