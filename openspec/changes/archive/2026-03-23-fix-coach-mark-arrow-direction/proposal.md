## Why

The coach mark arrow always curves to the upper-left regardless of the target's horizontal position, creating a visual disconnect when the target is to the right of the tooltip. The existing `onboarding-spotlight` spec already requires `position-try-fallbacks: flip-block, flip-inline`, but the implementation only uses `flip-block` — missing inline (horizontal) awareness entirely. This fix closes the spec-implementation gap and adds horizontal arrow mirroring so the arrow always curves toward the target.

## What Changes

- Add `flip-inline` and `flip-block flip-inline` to the CSS `position-try-fallbacks` (aligning implementation with existing spec)
- Change `position-area` from `block-end` to `block-end inline-start` to give the inline axis a direction that can be flipped
- Add CSS anchored container queries (`@container anchored (fallback: flip-inline)` and `flip-block flip-inline`) to detect horizontal flipping
- Mirror the arrow SVG via `transform: scaleX(-1)` when the tooltip flips inline, so the arrow curves toward the target
- Add a second set of dual-arrow HTML elements with mirrored SVG paths for the inline-flipped state (4 total arrow states: above/below x left/right)

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `onboarding-spotlight`: Add horizontal arrow direction awareness via CSS `flip-inline` anchored container query and SVG mirroring. Clarify 4-state arrow toggle (above-left, above-right, below-left, below-right) replacing the current 2-state (above/below) toggle.

## Impact

- **Frontend**: `coach-mark.css` (position-area, position-try-fallbacks, anchored container queries), `coach-mark.html` (arrow SVG mirroring via CSS transform — no HTML structure change needed if using `scaleX(-1)`)
- **Tests**: Unit tests for arrow visibility states; E2E visual verification of arrow direction across different target positions
- **No backend/API/protobuf changes**
