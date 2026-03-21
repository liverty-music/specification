## Context

The My Artists page currently renders artist hype settings as `<ul>/<li>` rows with a detached `<header class="hype-legend">` acting as a column header row. The two structures stay aligned only by sharing an identical `grid-template-columns: 2fr repeat(4, 1fr)` definition across three separate scopes (legend, row-content, hype-inline-slider). This is fragile and semantically incorrect.

The `hype-inline-slider` custom element wraps a `<fieldset>` that is used simultaneously as a CSS Grid container and a `position: relative` containing block for the decorative track line. Browser UA stylesheets apply an internal top padding to `<fieldset>` elements to accommodate `<legend>` placement — this cannot be fully reset with CSS — causing `inset-block-start: 50%` on the track element to resolve against the wrong height, producing the visible vertical offset bug.

The swipe-to-dismiss pattern uses `scroll-snap-type: x mandatory` on each `<li>`. This is incompatible with `<table><tr>` layout and is being removed in favour of an explicit delete `<button>` — a more discoverable and accessible interaction.

## Goals / Non-Goals

**Goals:**
- Replace `<ul>/<li>` + detached legend with a semantically correct `<fieldset>`-wrapped `<table>`
- Move `<thead>` column headers to where they belong, eliminating the legend/header sync problem
- Eliminate the `hype-slider-track` vertical offset bug by removing the `<fieldset>`-as-grid-container anti-pattern
- Preserve identical dot slider visuals (size, glow, pulse animation, 44px tap targets)
- Replace swipe-to-dismiss with a `<button>` delete action in the last `<td>` of each row
- Preserve Undo toast behaviour unchanged
- Preserve View Transition row removal animation (`view-transition-name` on `<tr>`)
- Delete `hype-inline-slider` component entirely

**Non-Goals:**
- No changes to hype RPC calls or backend
- No changes to onboarding spotlight targeting logic (target selector will change — see Risks)
- No Grid (Festival) view changes
- No new animations or visual redesign beyond parity with current dot style

## Decisions

### D1: `<fieldset>` wraps the entire `<table>`, not individual rows

**Decision**: One `<fieldset>` with `<legend class="visually-hidden">My Artists</legend>` wraps the whole `<table>`. Radio inputs within `<td>` cells share `name="hype-{artistId}"` for grouping.

**Why**: The memo.md pattern (notification settings) maps directly — `<fieldset>` labels the overall setting group; `<thead>/<th scope="col">` labels the columns; `<th scope="row">` labels each artist. This gives screen readers full row/column context automatically without any additional ARIA.

**Alternative considered**: One `<fieldset>` per artist row (wrapping the 4 radios). Rejected — this would nest `<fieldset>` inside `<td>`, which is valid HTML but loses the column-header association that `<table>` provides for free.

### D2: `hype-inline-slider` component is deleted, not kept as a thin wrapper

**Decision**: The component is deleted. Dot markup (`<label>/<input type="radio">/<span class="hype-dot">`) moves directly into each `<td>` in `my-artists-route.html`. Dot CSS moves into `my-artists-route.css`.

**Why**: The component's only job was to render 4 radio stops with a track line and dots. Inside a `<table>`, the `<td>` is the natural container — the component wrapper adds complexity with no benefit.

**Alternative considered**: Keep `hype-inline-slider` and render it inside `<td>`. Rejected — the fieldset/grid container issues would persist and the track alignment problem only moves, not disappears.

### D3: Track line rendered via `<td>::before` pseudo-element on hype cells

**Decision**: The decorative 2px track line is rendered as `::before` on each hype `<td>` (`.hype-col`), positioned absolutely from the dot center (`inset-inline-start: 50%`) with `inline-size: 100%`. This creates a chain of segments connecting adjacent dots. `z-index` keeps the line below the dot.

**Why**: `<tr>` pseudo-elements (`::before`/`::after`) have unreliable behaviour in the table anonymous-box structure — browsers may generate anonymous table cells around them, causing layout artifacts. `<td>` is a reliable `position: relative` containing block. `inset-block-start: 50%` resolves against the `<td>` height (not a `<fieldset>` UA-padded height), so vertical centering is exact.

**Alternative considered**: Track line as `<tr>::after` spanning hype columns. Rejected — `<tr>` pseudo-elements are placed inside table anonymous box structure and can produce unreliable containing blocks across browsers.

### D4: Delete action as `<button>` in final `<td>`, always visible

**Decision**: Each `<tr>` ends with a `<td class="artist-remove-col">` containing `<button type="button" aria-label="Remove {name}" click.trigger="unfollowArtist(artist)">`. The button is always visible (icon only, subtle colour until hover/focus).

**Why**: Swipe-to-dismiss has zero discoverability and is inaccessible to keyboard and AT users. An always-visible button solves both problems. The Undo toast (5s) already provides the safety net — no confirmation dialog needed.

**Alternative considered**: Keep swipe-to-dismiss alongside the button. Rejected — maintaining two deletion paths adds complexity and `scroll-snap` is incompatible with `<tr>`.

### D5: `<tbody><tr>` carries `view-transition-name`

**Decision**: `view-transition-name` is set via inline style `css="--_vt-name: artist-${artist.artist.id}"` on `<tr>`, and `view-transition-name: var(--_vt-name)` in CSS — identical to the current `<li>` pattern.

**Why**: View Transitions work on any element, not just `<li>`. The `startViewTransition` wrapper in `executeDismiss` remains unchanged.

## Risks / Trade-offs

- **Onboarding spotlight target changes** → The spotlight currently targets `.artist-list` (the `<ul>`). After this change, the equivalent is the `<table>` or `<tbody>`. The selector in `my-artists-route.ts` `activateSpotlight()` call must be updated. Low risk — single call site.

- **`<tr>` as `position: relative`** → CSS spec historically did not guarantee `position: relative` on `<tr>` creates a containing block. Modern browsers (Chrome 85+, Firefox 80+, Safari 16+) all support it. Given the PWA's minimum browser targets, this is safe.

- **`<table>` styling constraints** → `border-radius` on `<tr>` requires `border-collapse: separate` on `<table>`. The current card-style row borders need to move from `<li>` to `<tr>` with appropriate `border-spacing`.

- **`display: contents` on `<fieldset>` not needed** → Since `<fieldset>` wraps `<table>` (not acting as the grid container), the UA padding quirk does not apply. No `display: contents` workaround required.

## Migration Plan

1. Delete `src/components/hype-inline-slider/` (3 files)
2. Rewrite `my-artists-route.html` with the new `<fieldset>/<table>` structure
3. Rewrite `my-artists-route.css` — remove scroll-snap/dismiss styles, add table styles and dot CSS (moved from hype-inline-slider)
4. Update `my-artists-route.ts` — remove scroll-snap dismiss logic (`checkDismiss`, `executeDismiss`, `dismissingIds`); update `activateSpotlight` target selector
5. Update `openspec/specs/my-artists/spec.md` and `openspec/specs/hype-inline-slider/spec.md`

Rollback: revert the 3 changed files and restore the deleted component. No DB or API changes to roll back.

## Open Questions

_(none — all decisions resolved in exploration)_
