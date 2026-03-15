## Context

The bottom-nav-bar and page headers scroll with content on dashboard, my-artists, tickets, and settings pages. The existing specs (`app-shell-layout`, `shell-layout`) prescribe height containment via `au-viewport { display: grid }` in `app-shell.css`, but this approach has a fundamental flaw: it skips the route component CE boundary.

Investigation of Aurelia 2 source code (`packages/router/src/resources/viewport.ts`) confirmed that `au-viewport` is a template-less custom element. Routed components are attached via `appendChild`. As a CSS Grid item, `au-viewport` undergoes blockification and receives `align-self: stretch`, giving it a definite block-size without any explicit styling.

The current architecture violates CUBE CSS methodology by having `app-shell.css` style `au-viewport` and `live-highway` — components that should own their own display.

## Goals / Non-Goals

**Goals:**
- Fix header/footer scrolling on all route pages
- Establish a clear height-constraint chain from `app-shell` through every CE boundary
- Each route component declares its own layout structure via `:scope` with `grid-template-areas`
- Remove cross-component styling from `app-shell.css`
- Convert stale-banner from grid row to fixed overlay

**Non-Goals:**
- Extract shared `<page-header>` CE (follow-up task — reduces duplication but separate scope)
- Change app-shell grid to use `position: fixed` for bottom-nav-bar (current grid approach is correct)
- Modify any business logic or routing behavior

## Decisions

### D1: Route components declare `:scope` grid layout with `grid-template-areas`

Every route component starts with:
```css
:scope {
    display: grid;
    grid-template-areas: "header" "main";  /* varies per page */
    grid-template-rows: auto 1fr;
    block-size: 100%;
    min-block-size: 0;
}
```

**Why `block-size: 100%`**: `au-viewport` has a definite block-size from grid stretch. `100%` passes this through the CE boundary.

**Why `min-block-size: 0`**: Grid items default to `min-block-size: auto`, preventing shrink below content size. `0` allows descendants to activate `overflow`.

**Why `grid-template-areas`**: Makes layout structure self-documenting. A developer reads the CSS and immediately sees the page skeleton.

**Alternative considered**: `display: flex; flex-direction: column` — rejected because grid-template-areas provides better readability and flex-based layouts are what currently cause the confusion with orphaned `flex: 1` / `flex-shrink: 0` properties.

### D2: app-shell only styles itself

Remove `au-viewport { ... }` and `live-highway { ... }` rules. App-shell declares only:
```css
:scope {
    display: grid;
    grid-template-areas: "viewport" "nav";
    grid-template-rows: 1fr auto;
    block-size: 100dvh;
}
```

**Why not `minmax(0, 1fr)`**: With `min-block-size: 0` set on each route component's `:scope`, the min-content constraint is handled at each CE boundary rather than at the app-shell level. `1fr` is simpler and sufficient.

**Alternative considered**: Keep `au-viewport` styling but add route `:scope` — rejected because external CE styling is the root cause of fragility and CUBE CSS violations.

### D3: live-highway owns its display

Move from app-shell.css to live-highway.css `:scope`:
```css
:scope {
    display: block;
    block-size: 100%;
    min-block-size: 0;
}
```

### D4: Stale-banner becomes fixed overlay

The stale-data warning is a transient status notification (appears when API reload fails but cached data exists). It belongs alongside `toast-notification` and `error-banner` as an overlay, not a structural grid row.

- Use `position: fixed` with `inset-block-start: 0` and `inset-inline: 0`
- Add appropriate `z-index` to appear above content but below top-layer elements
- Dashboard grid simplifies to single area: `"main"`

### Height-Constraint Chain (after fix)

```
app-shell (grid, 100dvh)
  ├─ [area: viewport]  au-viewport (grid item → blockified, stretch)
  │    └─ <dashboard> :scope { grid, block-size: 100%, min-block-size: 0 }
  │         └─ [area: main]
  │              └─ <live-highway> :scope { block, block-size: 100%, min-block-size: 0 }
  │                   └─ .highway-layout (grid, block-size: 100%)
  │                        └─ .highway-scroll (overflow-block: auto) ← ACTIVATES
  └─ [area: nav]  <bottom-nav-bar> ← FIXED
```

## Risks / Trade-offs

- **[Risk] `1fr` instead of `minmax(0, 1fr)` at app-shell level** → Mitigated by `min-block-size: 0` on each route `:scope`. If a route forgets this, content could push nav-bar off screen. Playwright tests catch this.
- **[Risk] Stale-banner overlay occludes content** → Use `z-index` layering and auto-dismiss or manual dismiss. Existing toast-notification pattern already solves this.
- **[Risk] Discover page has different layout structure** → Requires investigation during implementation to determine correct `grid-template-areas`. Design pattern is the same; specific areas may differ.
