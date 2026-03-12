## Why

The frontend codebase relies on JavaScript-based patterns for positioning, animation timing, and scroll control that are now replaceable with 2026 Web Platform Baseline CSS features. These JS patterns (rAF loops, setTimeout for animation cleanup, getBoundingClientRect for position detection, scrollTop checks) cause layout thrashing, timing fragility, and unnecessary coupling between layout and logic. Modern CSS primitives handle these concerns declaratively and off the main thread.

## What Changes

- **Coach mark tooltip arrow**: Replace `getBoundingClientRect` + `rAF` arrow direction detection with Anchored Container Query (`@container anchored(fallback: flip-block)`) that toggles which SVG arrow is visible when the tooltip flips position — entirely in CSS, no JS state management
- **Coach mark scroll**: Replace `isInViewport()` layout-thrashing check with `scrollIntoView()` + `scrollend` event (browser decides if scroll is needed)
- **Toast notification entry**: Replace `requestAnimationFrame` entry animation trigger with CSS `@starting-style` for automatic enter animation on DOM insertion
- **Toast notification cleanup**: Replace `setTimeout(400)` DOM removal after exit animation with `transitionend` event listener for frame-accurate cleanup
- **Event detail sheet scroll chaining**: Add CSS `overscroll-behavior: contain` to prevent scroll events from leaking through the sheet to the page behind
- **Celebration overlay fade-out**: Replace `setTimeout(400)` fade-out cleanup with `transitionend` event listener

## Capabilities

### New Capabilities

_None — all changes are implementation-level modernization within existing components._

### Modified Capabilities

- `modern-css-platform`: Add requirements for Anchored Container Queries (`@container anchored()`), `@starting-style`, `transitionend`-based cleanup, `overscroll-behavior`, and `scrollIntoView` + `scrollend` patterns as standard practices. Prohibit `rAF`-based positioning, `setTimeout` for animation timing, and `getBoundingClientRect` for layout-dependent decisions that CSS can handle.

## Impact

- **Frontend only**: 4 components affected (`coach-mark`, `toast-notification`, `event-detail-sheet`, `celebration-overlay`)
- **No API/backend changes**: Pure presentation layer refactoring
- **No breaking changes**: External behavior unchanged; internal implementation modernized
- **Testing**: Unit tests updated to remove rAF mocking, add transitionend simulation
