## Why

The My Artists list view uses a `<ul>/<li>` structure with a separate sticky header (`hype-legend`) to represent what is fundamentally tabular data: artists (rows) × hype levels (columns) × radio selection (cells). This mismatch forces a fragile 3-layer CSS grid synchronisation to keep column alignment, introduces broken semantics (`<section>` without heading, `<header>` as a flex wrapper, `<div>` for an interactive dismiss action), and causes a persistent layout bug where the `hype-slider-track` is vertically offset due to `<fieldset>` UA stylesheet quirks. Replacing the structure with a semantic `<table>` wrapped in a `<fieldset>` resolves all of these issues at once.

## What Changes

- Replace `<ul class="artist-list">` + `<header class="hype-legend">` with a `<fieldset>`-wrapped `<table>` where `<thead>` carries the hype-level column headers and each `<tbody><tr>` is one artist row
- Remove the `hype-inline-slider` custom element; dot radio inputs move directly into table `<td>` cells, keeping identical visual style (dot glows, pulse animation, 44px tap targets)
- Remove swipe-to-dismiss (`scroll-snap-type`, `dismiss-end`, `checkDismiss`, `executeDismiss`, `dismissingIds`); replace with an explicit `<button>` in the final `<td>` of each row — Undo toast behaviour is preserved unchanged
- Fix `<section class="artist-row-content">` → `<div>` (layout wrapper, not a thematic region)
- Fix `<header class="artist-identity">` → `<div>` (not introductory content)
- Fix `<div class="dismiss-end">` → `<button type="button" aria-label="…">` (interactive element must be a button)
- **BREAKING**: `hype-inline-slider` component is deleted; any other consumer must migrate to the table cell pattern or a standalone radio group

## Capabilities

### New Capabilities

_(none — this is a refactor of existing UI)_

### Modified Capabilities

- `my-artists`: Row layout changes from scroll-snap `<li>` to `<tr>`; swipe-to-dismiss removed; delete button added to row
- `hype-inline-slider`: Component deleted; dot slider visual moved into `my-artists` table cells

## Impact

- **Deleted files**: `src/components/hype-inline-slider/` (3 files: `.ts`, `.html`, `.css`)
- **Modified files**: `src/routes/my-artists/my-artists-route.html`, `my-artists-route.css`, `my-artists-route.ts`
- **Spec updates**: `openspec/specs/my-artists/spec.md`, `openspec/specs/hype-inline-slider/spec.md`
- **No backend changes** — hype RPC calls remain identical
- **No routing changes**
