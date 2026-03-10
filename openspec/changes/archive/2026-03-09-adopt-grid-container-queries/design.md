## Context

The discover page (`discover-page.css`) uses 9 flex contexts to build a column layout: search bar → genre chips → bubble area / search results → onboarding HUD. The loading sequence page uses 3 more. The app shell (`my-app.css`) is the only component using CSS Grid (`grid-template-rows: 1fr min-content`).

The `modern-css-platform` spec mandates Container Queries for component-level responsive design, but only 2 files use `@container` today. The `app-shell-layout` spec already defines the grid-based shell — this change extends the grid pattern into route-level layouts.

## Goals / Non-Goals

**Goals:**
- Replace flex column layouts in discover and loading pages with CSS Grid explicit row tracks
- Introduce subgrid for `.result-item` alignment across the results list
- Add `container-type: inline-size` to key container elements for future `@container` adoption
- Maintain all existing Playwright layout assertions (bounding box relationships must not change)

**Non-Goals:**
- Migrating modal/dialog layouts (fixed/absolute positioning is appropriate for overlays)
- Adding new `@container` responsive breakpoint rules (this change adds the container declarations; responsive rules come in follow-up work)
- Changing the app shell grid structure (already correct per spec)
- Modifying HTML templates or TypeScript code

## Decisions

### 1. Grid row tracks mirror the existing flex structure

The discover page flex column has a clear implicit track structure:

```
/* Current flex approach */
.discover-layout { display: flex; flex-direction: column; }
.search-bar      { flex-shrink: 0; }          /* fixed height */
.genre-chips     { flex-shrink: 0; }          /* fixed height */
.bubble-area     { flex: 1; min-height: 0; }  /* fills remaining */

/* Grid replacement */
.discover-layout {
  display: grid;
  grid-template-rows: auto auto 1fr;
}
```

**Why grid over flex:** Explicit row tracks eliminate the need for `flex-shrink: 0` on every non-growing child. The `1fr` track is self-documenting — it communicates "this row gets remaining space" more clearly than `flex: 1; min-height: 0`.

**Alternative considered:** Keep flex and add `container-type` only. Rejected because the flex + `flex-shrink: 0` pattern is fragile — adding a new row requires remembering to set shrink, and `min-height: 0` on the growing row is a non-obvious workaround for flex overflow.

### 2. Subgrid for search result items

```
.results-list {
  display: grid;
  grid-template-columns: auto 1fr auto;
}
.result-item {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
}
```

**Why subgrid:** Avatar (fixed width), name (flexible), and follow button (fixed width) columns align across all result items without per-item flex calculations. This eliminates `min-width: 0` hacks for text truncation.

**Alternative considered:** Keep flex with fixed widths. Rejected because avatar and button sizing already uses fixed `width` values — subgrid formalizes this into a shared column definition.

### 3. Container declarations without responsive rules

Add `container-type: inline-size` to `.search-results` and `.bubble-area`. Do NOT add `@container` rules in this change.

**Why separate:** Container type declaration is a zero-cost addition (browsers only create a containment context, no layout change). Adding responsive `@container` rules requires design decisions about breakpoints and layout variations — that belongs in a follow-up change.

### 4. Loading page grid centering

```
/* Current */
.loading-layout { display: flex; flex-direction: column; align-items: center; justify-content: center; }

/* Replacement */
.loading-layout { display: grid; place-items: center; }
```

**Why:** `place-items: center` is a single declaration that replaces three flex properties. Grid centering also handles the case where content exceeds the container more predictably than flex centering.

## Risks / Trade-offs

- **Layout assertion failures** → Run `npx playwright test e2e/layout/` after each file change. The tests verify bounding box relationships, not CSS implementation details, so they should pass. If any fail, investigate before proceeding.
- **Subgrid browser support** → Subgrid is Baseline 2023. All target browsers support it. No `@supports` fallback needed.
- **Onboarding HUD absolute positioning** → The HUD and complete button use `position: absolute` within `.bubble-area`. Converting `.bubble-area` to a grid child does not affect absolute positioning of its descendants (absolutely positioned elements are removed from flow regardless of parent layout mode).
