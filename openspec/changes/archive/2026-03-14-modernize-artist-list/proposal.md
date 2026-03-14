## Why

The My Artists list view has two structural problems rooted in excessive DOM nesting:

1. **Hype header-to-slider misalignment** — The header emoji columns and slider dots use independent grid contexts at different DOM depths, so their column lines never match.
2. **JS-driven swipe** — Swipe-to-unfollow uses manual `touchstart`/`touchmove`/`touchend` handlers with per-frame `transform` updates on the main thread. This requires a clip wrapper (`artist-list-item`) and an absolute-positioned delete zone behind each row, adding 2 unnecessary DOM layers and blocking compositor-thread optimization.

Both problems disappear by flattening the DOM and adopting modern Web Platform primitives: CSS `scroll-snap` for swipe, `grid-template-areas` for column alignment, and View Transitions API for dismiss animation.

## What Changes

- **Flatten DOM**: Remove `.artist-list-inner` (padding-only wrapper) and merge `.artist-list-item` + `.artist-row` into a single `.artist-row` element
- **Replace JS swipe with scroll-snap**: Each `.artist-row` becomes a horizontal scroll container with `scroll-snap-type: x mandatory`. A `.dismiss-end` element replaces the absolute-positioned `.delete-zone`
- **Remove all touch handlers**: Delete `onTouchStart`, `onTouchMove`, `onTouchEnd`, `swipeOffset`, `swipedArtistId`, and long-press timer logic
- **Add View Transitions dismiss animation**: Use `document.startViewTransition()` for smooth list reflow when an artist is removed
- **Align columns with `grid-template-areas`**: Header and artist-row-content share `2fr repeat(4, 1fr)` with named areas `"name watch home nearby away"`
- **Remove long-press unfollow**: Swipe-to-dismiss is the only unfollow gesture in list view

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hype-inline-slider`: Header and slider column alignment now enforced via shared grid-template-columns with named areas
- `my-artists`: Artist row structure changes — swipe-to-unfollow moves from JS touch handlers to CSS scroll-snap; long-press unfollow removed from list view; View Transitions dismiss animation added

## Impact

- `frontend/src/routes/my-artists/my-artists-page.html` — DOM restructure (flatten 2 layers), replace touch bindings with scroll event
- `frontend/src/routes/my-artists/my-artists-page.css` — New grid layout, scroll-snap styles, remove delete-zone/swipe styles
- `frontend/src/routes/my-artists/my-artists-page.ts` — Remove touch handlers, swipe state, long-press logic; add scroll-based dismiss + View Transitions
- `frontend/src/components/hype-inline-slider/hype-inline-slider.css` — No changes (internal grid unchanged)
