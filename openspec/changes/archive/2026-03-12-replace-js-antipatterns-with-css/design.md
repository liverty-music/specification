## Context

The frontend uses four JS-based patterns that modern CSS (2026 Baseline) handles natively:

1. **`rAF` + `getBoundingClientRect` for position detection** — coach-mark arrow direction was determined by reading computed layout in a `requestAnimationFrame` callback, causing forced reflows
2. **`rAF` for entry animation triggering** — toast notification used `requestAnimationFrame` to defer `visible = true` so the browser could register the initial state before animating
3. **`setTimeout` for post-animation cleanup** — toast and celebration overlay used hardcoded `setTimeout(400)` to remove DOM elements after CSS transitions, creating timing fragility
4. **`scrollTop > 0` for scroll position checks** — event detail sheet reads `scrollTop` to decide whether a drag gesture should be treated as drag-to-dismiss or content scroll

## Goals / Non-Goals

**Goals:**
- Replace all `rAF`-based positioning and animation triggering with CSS-native equivalents
- Replace all `setTimeout`-based animation cleanup with `transitionend` event listeners
- Add `overscroll-behavior: contain` where appropriate to prevent scroll chaining
- Use Anchored Container Queries (`@container anchored()`) for position-dependent child styling (arrow toggle)
- Use `@starting-style` for entry animations on dynamically inserted elements
- Use `scrollIntoView` + `scrollend` instead of manual viewport detection

**Non-Goals:**
- Replacing the `scrollTop > 0` drag gesture check — this is JS gesture recognition logic, not a layout concern; CSS cannot determine whether a touch gesture should be intercepted
- Replacing `matchMedia('prefers-reduced-motion')` for JS timer duration — JS needs the boolean value to choose between timer durations; this is not a CSS concern
- Changing the display timer `setTimeout` in celebration overlay — the delay before starting fade-out is business logic (how long to show), not animation timing

## Decisions

### Decision 1: Anchored Container Query for arrow toggle

**Choice:** Use `container-type: anchored` on the tooltip and `@container anchored(fallback: flip-block)` to toggle which of the two SVG arrows is visible. The built-in `flip-block` keyword replaces a custom `@position-try` rule, and the anchored container query lets child elements query which fallback was applied — entirely in CSS.

**Why:** `@position-try` (Anchor Positioning L1) cannot change layout properties like `display` or `flex-direction`, and custom properties set inside `@position-try` do not cascade to descendant elements. Anchored Container Queries (Anchor Positioning L2, Chrome 143+) solve this by exposing the resolved fallback state as a container query condition, letting children adapt their styles without JS.

**Alternatives considered:**
- `@position-try` with `--arrow-rotation` custom property + `transform: rotate()` — rejected because custom properties set in `@position-try` do not cascade to child elements, making it impossible to rotate a nested SVG arrow.
- JS `detectFlip()` with double `requestAnimationFrame` + `data-flipped` attribute — rejected because it forces layout reads on the main thread and adds JS state for a purely visual concern.
- `@container style()` queries on `@position-try` custom properties — rejected because `@position-try` custom properties do not appear in `getComputedStyle()` and cannot be queried by style container queries.

### Decision 2: `@starting-style` for entry animations

**Choice:** Use `@starting-style` nested inside the element's rule block to define initial values (`opacity: 0`, `translateY(-1rem)`) that the browser automatically transitions from on DOM insertion.

**Why:** `@starting-style` (Baseline 2024) triggers automatically when an element enters the DOM, eliminating the need for `rAF` to defer state changes. Already used in `event-detail-sheet.css` — this decision extends the pattern to `toast-notification`.

**Alternative considered:** `animation` keyframes — rejected because `@starting-style` integrates with `transition` (which the exit animation already uses), keeping enter/exit as symmetric operations on the same properties.

### Decision 3: `transitionend` for post-animation DOM cleanup

**Choice:** Listen for `transitionend` on the host element (event delegation via bubbling) and remove DOM elements only after the CSS transition completes. Match by `propertyName === 'opacity'` and `target.dataset.toastId`.

**Why:** Directly tied to the actual transition end, not a hardcoded timeout. Immune to timing drift if transition durations change in CSS.

**Alternative considered:** `MutationObserver` — rejected as over-engineering. `transitionend` is the natural event for "animation just finished."

### Decision 4: `overscroll-behavior: contain` for scroll isolation

**Choice:** Apply `overscroll-behavior: contain` on the scrollable content area inside the event detail sheet.

**Why:** Prevents scroll events from propagating to the page behind the sheet (scroll chaining). This is a CSS-level scroll boundary, complementary to the JS `scrollTop` check which handles drag gesture detection.

### Decision 5: `scrollIntoView` + `scrollend` replaces `isInViewport()`

**Choice:** Always call `scrollIntoView({ behavior: 'smooth', block: 'center' })` and wait for the `scrollend` event (with an 800ms failsafe timeout) before showing the spotlight.

**Why:** `scrollIntoView` is a no-op when the element is already visible — the browser handles the viewport check internally. Eliminates `getBoundingClientRect` and the `isInViewport()` helper entirely.

## Risks / Trade-offs

- **Anchored Container Query browser support**: Chrome 143+ (October 2025), Edge 143+. No Firefox or Safari support yet (~63.5% global coverage). Our PWA targets Chromium-based mobile browsers → acceptable.
  → Mitigation: Without `container-type: anchored`, the default arrow (`.coach-arrow-above`) is always shown. The tooltip still flips via `flip-block`, only the arrow toggle is lost.

- **`transitionend` may not fire if `transition: none`**: Under `prefers-reduced-motion: reduce`, transitions are disabled.
  → Mitigation: `celebration-overlay` already short-circuits to immediate cleanup when `prefersReducedMotion()` is true, bypassing the `transitionend` path. Toast notification uses `@media (prefers-reduced-motion: reduce) { transition: none; }` — the `setTimeout` duration fallback still cleans up via the dismiss timer.

- **`scrollend` event**: Baseline 2024. Not all browsers fire it in all cases (e.g., when no scroll occurs).
  → Mitigation: 800ms failsafe `setTimeout` resolves the promise if `scrollend` never fires.
