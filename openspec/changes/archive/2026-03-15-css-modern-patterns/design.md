## Context

The `modern-css-platform` spec defines requirements for Container Queries, View Transitions, `:has()`, `@starting-style`, and Anchor Positioning. After `css-state-separation` cleaned up TS/CSS responsibility leaks and `extract-shared-components` created shared UI primitives, this change focuses on adopting modern CSS patterns that further reduce JavaScript involvement in presentation. The most impactful change is replacing the event-detail-sheet's JS touch drag dismiss with CSS scroll snap.

## Goals / Non-Goals

**Goals:**
- Replace event-detail-sheet's JS drag-to-dismiss with CSS scroll snap + `scrollend` event
- Delete dead custom attributes (`SwipeOffsetCustomAttribute`, `DragOffsetCustomAttribute`)
- Replace `requestAnimationFrame` entry animation deferrals with `@starting-style`
- Adopt CSS `:has()` for parent-state styling where JS class toggling exists
- Replace JS scroll listeners with Scroll-driven Animations where applicable
- Ensure all responsive components use Container Queries (audit for gaps)

**Non-Goals:**
- Redesigning the visual appearance of components
- Adding new UI components
- Changing the component architecture or state management
- Polyfilling for browsers below 2026 Baseline
- Adopting external libraries (pure-web-bottom-sheet, etc.)

## Decisions

### Decision 1: CSS scroll snap dismiss (self-implemented)

Replace the JS touch drag dismiss in event-detail-sheet with CSS scroll snap:

```
Before:
  dialog
  └── .sheet-body (overflow-y: auto, max-block-size: 70vh)
      └── .sheet-content

  touchstart → touchStartY
  touchmove  → deltaY → dragOffset → custom attr → CSS var → translate
  touchend   → threshold → close() or reset
  JS: ~30 lines + custom attribute: ~30 lines

After:
  dialog
  └── .sheet-wrapper (overflow-y: auto, scroll-snap-type: y mandatory,
  │                   overscroll-behavior: contain)
  │   ├── .sheet-body (scroll-snap-align: start)
  │   └── .dismiss-zone (scroll-snap-align: end)

  scrollend → scrollTop > threshold → close()
  JS: ~5 lines
```

**Why self-implement instead of pure-web-bottom-sheet:**
- event-detail-sheet has unique requirements: dynamic `popover="auto"/"manual"` for onboarding, `history.pushState` URL management, `toggle` event for light dismiss, `artist-color` custom attribute integration
- Library uses Shadow DOM which creates Aurelia binding and CUBE CSS styling barriers
- Library is pre-1.0 (v0.3.0) with breaking change risk
- The actual CSS needed is ~15 lines of scroll snap properties — the abstraction provides no value

**Why `scrollend` over `scrollsnapchange`:**
- `scrollend` is Baseline 2025 (Dec) — all browsers
- `scrollsnapchange` is experimental — Chrome 129+ only, not Baseline

**Why removing `overflow-y: auto` is safe:**
- Sheet content: artist name (1-2 lines) + event title + date + venue + 2 buttons
- Total height never approaches 70vh
- The `scrollTop > 0` check in current TS is defensive code that never fires

### Decision 2: @starting-style for entry animations

Elements inserted into the DOM dynamically SHALL use `@starting-style` for entry animations instead of `requestAnimationFrame` or two-step class toggling. This is already partially adopted (event-detail-sheet popover uses `@starting-style`); extend to all dynamic content.

### Decision 3: CSS :has() for parent-state styling

Parent elements that need to change style based on child state SHALL use `:has()`. This replaces patterns where TS sets a class on the parent when a child's state changes.

### Decision 4: Custom attribute bridge elimination

Custom attributes that solely bridge JS values to CSS custom properties (`--_drag-y`, `--_swipe-x`) are an unnecessary abstraction layer. These SHALL be deleted when the underlying JS pattern is replaced (scroll snap for drag, unused for swipe).

Custom attributes that perform computation (e.g., `artist-color` which hashes an artist name to a hue value) remain valid and are out of scope.

## Risks / Trade-offs

- [Risk] Removing `overflow-y: auto` from sheet-body means extremely long content would be clipped → Mitigated: content is fixed structure (artist name, date, venue, 2 buttons), max height is bounded
- [Risk] `scrollend` may not fire if user lifts finger before scroll momentum completes on some older mobile browsers → Mitigated: Baseline 2025, and scroll snap ensures the container snaps to a defined position regardless
- [Risk] Scroll-driven Animations are Baseline 2024 (December) — some older mobile browsers may not support them → Use `@supports (animation-timeline: scroll())` feature query with graceful degradation
- [Risk] `:has()` has slight performance implications with deeply nested selectors → Limit depth to 1-2 levels
