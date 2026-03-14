## Why

Overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) participate in the `my-app` CSS Grid as implicit row items, pushing `bottom-nav-bar` out of its intended `min-content` row. This breaks two things: (1) the bottom nav disappears off-viewport and only appears when scrolling to the very end, and (2) the `live-highway` scroll container loses its height constraint so the stage header's `position: sticky` has no effect.

## What Changes

- Remove overlay elements from normal grid flow so they no longer create implicit grid rows.
- Ensure `my-app`'s two-row grid (`1fr` + `min-content`) contains exactly `au-viewport` and `bottom-nav-bar`.
- Stage header sticky positioning will work correctly once the scroll container is properly height-constrained.
- No HTML changes required — CSS-only fix.

## Capabilities

### New Capabilities

_(none — this is a bug fix, not a new capability)_

### Modified Capabilities

_(no spec-level behavior changes — the layout was always intended to work this way)_

## Impact

- **File**: `src/my-app.css` — overlay element styles change from `block-size: 0` collapse to `position: fixed` flow removal.
- **Affected components**: `bottom-nav-bar` (will stay pinned at viewport bottom), `live-highway` stage header (sticky will function), `coach-mark` (needs to be added to the overlay exclusion list).
- **Risk**: Low — overlay elements already use top-layer APIs (popover/dialog), so removing them from flow has no visual side effects.
