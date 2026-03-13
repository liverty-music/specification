## Why

After `css-cleanup` (lint hardening) and `css-state-separation` (TS/CSS responsibility split), the codebase is ready to adopt 2026 Web Platform Baseline CSS features that replace remaining JavaScript-based patterns. Container Queries are specified but not fully utilized. Scroll-driven Animations, CSS `:has()` for parent-state styling, and `@starting-style` for entry animations are available but not yet adopted. These features eliminate JavaScript scroll listeners, class-toggling for parent state, and `requestAnimationFrame` deferrals — moving the work to the compositor thread for better performance.

## What Changes

- **Container Queries full adoption**: Audit all components for responsive breakpoints and convert remaining fixed layouts to container-query-driven responsive designs
- **CSS `:has()` for parent-state styling**: Replace JS-driven parent class toggling with `:has()` selectors (e.g., nav item active state, form validation feedback)
- **Scroll-driven Animations**: Replace JS scroll listeners with `animation-timeline: scroll()` for scroll-linked effects (parallax, progress indicators)
- **`@starting-style` for entry animations**: Replace `requestAnimationFrame` deferrals for newly inserted DOM elements with `@starting-style` declarations
- **Anchor Positioning refinements**: Expand CSS Anchor Positioning usage beyond coach-mark, using `position-area` and `position-try-fallbacks` for tooltips and popovers

## Capabilities

### New Capabilities

(none — all features are already specified in `modern-css-platform`)

### Modified Capabilities

- `modern-css-platform`: Add Scroll-driven Animations requirement; strengthen Container Queries requirement to cover all responsive components

## Impact

- **frontend**: Component CSS files that use JS scroll listeners, `requestAnimationFrame` for entry animations, or JS-driven parent class toggling. Key components: `live-highway`, `dashboard`, `my-artists-page`, `event-detail-sheet`
- **specification**: Delta spec for `modern-css-platform`
