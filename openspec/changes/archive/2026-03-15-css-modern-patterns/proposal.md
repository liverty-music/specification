## Why

After `css-cleanup` (lint hardening), `css-state-separation` (TS/CSS responsibility split), and `extract-shared-components` (shared UI components), the codebase is ready to adopt 2026 Web Platform Baseline CSS features that replace remaining JavaScript-driven presentation patterns. The event-detail-sheet still uses JS touch handlers + custom attributes for drag-to-dismiss — this can be replaced entirely with CSS scroll snap. Several custom attributes exist solely as JS→CSS variable bridges that should be eliminated. Other modern CSS features (Scroll-driven Animations, `:has()`, `@starting-style`, Container Queries) are specified but not yet adopted where applicable.

## What Changes

- **CSS scroll snap dismiss for event-detail-sheet**: Replace JS touch drag handlers (`onTouchStart`/`onTouchMove`/`onTouchEnd`) and `DragOffsetCustomAttribute` with CSS scroll snap + `scrollend` event. Remove `.sheet-body` `overflow-y: auto` (content never exceeds viewport). Self-implemented, not using external library (pure-web-bottom-sheet rejected due to integration cost with existing popover/history/onboarding logic).
- **Dead custom attribute cleanup**: Delete `SwipeOffsetCustomAttribute` (orphaned, zero usage in HTML) and `DragOffsetCustomAttribute` (replaced by scroll snap)
- **`@starting-style` for entry animations**: Replace any `requestAnimationFrame` deferrals with `@starting-style` declarations for popover/toast entry animations
- **CSS `:has()` for parent-state styling**: Replace JS-driven parent class toggling with `:has()` selectors where applicable
- **Scroll-driven Animations**: Replace JS scroll listeners with `animation-timeline: scroll()` for scroll-linked visual effects where applicable
- **Container Queries full coverage**: Audit and convert remaining viewport-based `@media` queries to `@container` queries in component CSS

## Capabilities

### New Capabilities

(none — all features are already specified in `modern-css-platform`)

### Modified Capabilities

- `modern-css-platform`: Add CSS scroll snap dismiss requirement; add custom attribute bridge elimination requirement; strengthen Container Queries requirement to cover all responsive components

## Impact

- **frontend**: `event-detail-sheet` (scroll snap dismiss rewrite), `drag-offset.ts` and `swipe-offset.ts` custom attributes (deletion), `main.ts` (registration cleanup), component CSS files using JS scroll listeners or `requestAnimationFrame` for entry animations
- **specification**: Delta spec for `modern-css-platform`
