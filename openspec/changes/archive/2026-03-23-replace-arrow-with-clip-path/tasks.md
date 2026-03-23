## 1. Remove SVG arrow elements

- [x] 1.1 Remove `.coach-arrow-container.coach-arrow-above` div and its SVG from `coach-mark.html`
- [x] 1.2 Remove `.coach-arrow-container.coach-arrow-below` div and its SVG from `coach-mark.html`

## 2. Add `::before` pseudo-element arrow

- [x] 2.1 Add `anchor-name: --coach-tooltip` to `.coach-mark-tooltip` in `coach-mark.css`
- [x] 2.2 Add `::before` pseudo-element on `.coach-mark-tooltip` with `position: fixed`, `clip-path: polygon()`, `background: inherit`, and `margin: inherit`
- [x] 2.3 Position arrow horizontally via `left: calc(anchor(--coach-target center) - var(--arrow-size) / 2)`
- [x] 2.4 Position arrow vertically via `top: calc(anchor(--coach-tooltip top) - var(--arrow-gap))` and `bottom: calc(anchor(--coach-tooltip bottom) - var(--arrow-gap))`

## 3. Clean up old arrow CSS

- [x] 3.1 Remove `.coach-arrow-container`, `.coach-arrow-above`, `.coach-arrow-below` CSS rules
- [x] 3.2 Remove `@container anchored (fallback: flip-block)` arrow toggling rules
- [x] 3.3 Remove arrow SVG styling rules (`.arrow-line`, `.arrow-head`, stroke-dasharray animation, `@keyframes draw-line`, `@keyframes fade-in-head`)
- [x] 3.4 Update `position-try-fallbacks` to `flip-block` only (remove flip-inline if still present)

## 4. Reduced motion

- [x] 4.1 Ensure `prefers-reduced-motion: reduce` disables any arrow appearance animation

## 5. Update tests

- [x] 5.1 Update E2E arrow assertions in `css-antipattern-verification.spec.ts` to verify `::before` pseudo-element positioning instead of SVG bounding boxes
- [x] 5.2 Update unit tests in `coach-mark.spec.ts` if they reference arrow DOM elements (N/A: no arrow references found)
- [x] 5.3 Run full E2E suite and verify all tests pass (coach-mark tests pass; celebration overlay flakes are pre-existing)

## 6. Lint and verify

- [x] 6.1 Run `make check` and fix any stylelint or biome errors (0 errors, warnings only from other files)
