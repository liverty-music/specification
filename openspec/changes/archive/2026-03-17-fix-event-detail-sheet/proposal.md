## Why

The event detail bottom sheet has two visual/interaction bugs:

1. The sheet floats in the vertical center of the viewport instead of anchoring to the bottom edge. This is caused by the browser's UA stylesheet for `[popover]:popover-open` (`inset: 0; margin: auto`) overriding the component's layered CSS (`@layer block`). Initial investigation showed the `user-home-selector` pattern (higher-specificity selector, explicit `translate`) was insufficient — the dismiss zone's height within the scroll container caused the card to visually "float" regardless of positioning overrides.

2. The swipe-to-dismiss gesture has an extremely narrow effective area limited to the small handle bar padding (~20px). Users expect to be able to pull down from anywhere on the sheet body to dismiss it.

## What Changes

- Adopt a "Fullscreen Snap Architecture": the dialog fills the entire viewport (`inset: 0; 100dvh`), with two 100dvh snap pages (dismiss zone above, card pinned to bottom via `flex-end` below). This eliminates the visual centering bug by decoupling the card's visual boundary from the popover's layout boundary.
- Expand the swipe-to-dismiss touch target to cover the entire dialog surface, not just the handle bar area.
- Add real-time backdrop fade-out during dismiss scroll, unifying the visual feedback for both swipe and tap dismiss.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-detail`: Clarify swipe-to-dismiss requirement — the entire sheet surface (not just the handle) should be the drag target for pull-to-dismiss.

## Impact

- **Frontend**: CSS, HTML, and TypeScript changes in `src/components/live-highway/event-detail-sheet.*`.
  - CSS: Fullscreen dialog, scroll snap pages, flex-end card positioning.
  - HTML: Added snap-page wrappers, reordered dismiss-zone above card, added `scroll` event listener.
  - TS: Added `onScroll()` for real-time backdrop opacity, changed `onBackdropClick()` to use smooth scroll dismiss, `onScrollEnd()` threshold updated for reversed page order.
- No backend, API, or proto changes required.
