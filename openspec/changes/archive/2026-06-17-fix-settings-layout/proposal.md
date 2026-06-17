## Why

The Settings page ships with a layout regression: the first preferences card is
clipped behind the fixed `page-header` — the PREFERENCES section title and the
first rows (My Home Area, Language) render under the header instead of inside
the scroll area.

The Settings `main` is itself the scroll container (`overflow-y: auto`) but
omits `min-block-size: 0`. As a grid item in the `1fr` content track its default
`min-block-size: auto` prevents it from shrinking below its content height, so
the track grows past the route's `100%` box, the grid overflows, and the content
slides under the header. Every sibling route (my-artists, dashboard, tickets,
discovery) keeps `main` as an `overflow: hidden` shell with an inner scroll
child (using `min-block-size: 0` or a `block-size: 100%` child to bound the
track) — Settings is the only route that diverged. That divergence also left
CUBE CSS drift in the page (composition re-implemented in the block layer;
misused bracket grouping).

> Out of scope: the guest language-selector reactivity defect (the selector
> highlight not following the active locale) is tracked separately and will be
> fixed as part of the GuestService dissolution refactor, not here.

## What Changes

- **Fix the scroll/layout regression.** Re-align Settings with the house scroll
  pattern: `main` becomes an `overflow: hidden` shell with `min-block-size: 0`,
  and an inner scroll container (`flex: 1; overflow-y: auto`) holds the section
  list — matching my-artists / tickets / dashboard / discovery. The fixed
  `page-header` stays pinned; the section list scrolls within the content area.
- **Re-use CUBE composition primitives.** The vertical section list uses the
  existing `[ stack ]` composition (compositions.css) for its rhythm instead of
  re-declaring flex+gap in the block layer; the language list likewise.
- **Correct CUBE bracket-grouping usage.** Remove the meaningless single-block
  bracket wrapper `class="[ settings-divider ]"`; apply bracket grouping only
  where it expresses `[ block ] [ composition ] [ utilities ]` role grouping.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `settings`: adds a layout/scroll requirement for the Settings page content
  area (fixed header + scrollable list that does not overlap the header).

## Impact

- **Frontend only.** Touches `src/routes/settings/settings-route.{css,html}`.
  No TypeScript/ViewModel, backend, proto, or DB changes; no new dependencies.
- **CUBE CSS alignment.** Brings Settings in line with `cube-css-architecture`,
  `cube-css-structural-rules`, and `cube-css-layer-constraints` (composition
  re-use, layer placement, bracket grouping).
- **Tests.** Visual/layout assertion that the first row is visible (not clipped
  by the header). The existing `settings.auth.visual.spec.ts` screenshot
  baseline will need to be refreshed.
- **Ships to prod** as part of the normal frontend release (GitHub Release →
  prod AR retag → cloud-provisioning prod pin bump).
