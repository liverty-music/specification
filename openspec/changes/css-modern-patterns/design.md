## Context

The `modern-css-platform` spec already defines requirements for Container Queries, View Transitions, `:has()`, `@starting-style`, and Anchor Positioning. After `css-state-separation` cleans up TS/CSS responsibility leaks, this change focuses on adopting additional modern CSS patterns that further reduce JavaScript involvement in presentation concerns.

## Goals / Non-Goals

**Goals:**
- Replace all JS scroll listeners with Scroll-driven Animations (`animation-timeline: scroll()`)
- Replace `requestAnimationFrame` entry animation deferrals with `@starting-style`
- Adopt CSS `:has()` for parent-state styling where JS class toggling was previously required
- Ensure all responsive components use Container Queries (audit for gaps)
- Expand Anchor Positioning beyond coach-mark to tooltips and dropdowns

**Non-Goals:**
- Redesigning the visual appearance of components
- Adding new UI components
- Changing the component architecture or state management
- Polyfilling for browsers below 2026 Baseline

## Decisions

### Decision 1: Scroll-driven Animations over JS scroll listeners

Use `animation-timeline: scroll()` and `animation-timeline: view()` for:
- Progress indicators that track scroll position
- Parallax effects on scrollable content
- Sticky header shadow that appears on scroll

JS scroll listeners (`addEventListener('scroll', ...)`) SHALL be removed and replaced with pure CSS. This moves the work to the compositor thread, eliminating jank.

**Alternative**: `IntersectionObserver` for enter-viewport effects. Still valid for non-animation triggers (lazy loading, analytics), but animation-linked effects belong in CSS.

### Decision 2: @starting-style for entry animations

Elements inserted into the DOM (via `if.bind`, `repeat.for`, or popover) SHALL use `@starting-style` to define their initial animation state:

```css
.toast-item {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms, transform 300ms;

  @starting-style {
    opacity: 0;
    transform: translateY(-1rem);
  }
}
```

This replaces the pattern of using `requestAnimationFrame` to add an animation class after DOM insertion.

### Decision 3: CSS :has() for parent-state styling

Parent elements that need to change style based on child state SHALL use `:has()`:

```css
.nav-tab:has([data-active]) {
  color: var(--color-text-primary);
}
```

This replaces patterns where TS sets a class on the parent when a child's state changes.

## Risks / Trade-offs

- [Risk] Scroll-driven Animations are Baseline 2024 (December) — some older mobile browsers may not support them → Use `@supports (animation-timeline: scroll())` feature query with graceful degradation (static fallback)
- [Risk] `@starting-style` requires the element to have a `transition` — if transition is removed (e.g., reduced motion), entry animation silently disappears → This is correct behavior; `prefers-reduced-motion` should disable entry animations
- [Risk] `:has()` has slight performance implications with deeply nested selectors → Limit `:has()` depth to 1-2 levels; avoid `:has(> * > * > .target)` patterns
