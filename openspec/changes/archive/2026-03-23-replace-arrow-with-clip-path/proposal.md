## Why

The coach-mark arrow uses two SVG elements with hardcoded left-curving paths. Because SVG curves are asymmetric, the arrow points away from the target when the target is on certain sides of the tooltip. CSS Anchor Positioning cannot detect horizontal spatial relationships to mirror the SVG, and the `flip-inline` workaround caused tooltip position drift. The community best practice is to use `::before` pseudo-elements with `clip-path: polygon()` for symmetric triangular arrows that work with `position-try-fallbacks` out of the box.

## What Changes

- Remove the two `coach-arrow-container` SVG divs from `coach-mark.html`
- Replace with a `::before` pseudo-element on `.coach-mark-tooltip` using `clip-path: polygon()` to create a symmetric triangular arrow
- Position the arrow via `anchor(--coach-target center)` to always point at the target center
- Use `margin: inherit` pattern so `flip-block` automatically flips the arrow direction
- Remove arrow-related `@container anchored` rules (visibility toggling no longer needed)
- Update E2E tests to verify the new arrow element (pseudo-element bounding box checks)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-spotlight`: Arrow rendering changes from SVG elements to CSS pseudo-element with clip-path

## Impact

- `frontend/src/components/coach-mark/coach-mark.html` — remove 2 SVG arrow divs
- `frontend/src/components/coach-mark/coach-mark.css` — replace arrow styles with `::before` + `clip-path`
- `frontend/e2e/css-antipattern-verification.spec.ts` — update arrow assertions
- `frontend/test/components/coach-mark.spec.ts` — remove arrow-related DOM assertions if any
