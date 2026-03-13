## 1. Audit current JS-driven patterns

- [ ] 1.1 Grep for `addEventListener('scroll'` and `scroll` event listeners — identify candidates for Scroll-driven Animations
- [ ] 1.2 Grep for `requestAnimationFrame` used for entry animation deferrals — identify candidates for `@starting-style`
- [ ] 1.3 Grep for parent class/attribute toggling driven by child state — identify candidates for CSS `:has()`
- [ ] 1.4 Grep for `@media (min-width` or `@media (max-width` in component CSS — identify remaining viewport queries to convert

## 2. Scroll-driven Animations

- [ ] 2.1 Replace JS scroll listeners with `animation-timeline: scroll()` for scroll-linked effects
- [ ] 2.2 Add `@supports (animation-timeline: scroll())` feature queries for graceful degradation
- [ ] 2.3 Remove corresponding JS scroll event listeners and cleanup functions

## 3. @starting-style for entry animations

- [ ] 3.1 Add `@starting-style` to toast notification entry animation, remove `requestAnimationFrame` deferral if present
- [ ] 3.2 Add `@starting-style` to popover entry animations, remove `requestAnimationFrame` deferral if present
- [ ] 3.3 Add `@starting-style` to dynamically inserted list items (repeat.for) that have entry animations

## 4. CSS :has() for parent-state styling

- [ ] 4.1 Refactor navigation active state: use `:has([data-active])` on parent instead of JS parent class toggle
- [ ] 4.2 Refactor form validation: use `:has(:invalid)` on parent group instead of JS validation watcher
- [ ] 4.3 Identify and refactor any other parent-child state patterns

## 5. Container Queries full coverage

- [ ] 5.1 Audit all components for responsive layout — ensure every responsive component uses `@container` not `@media`
- [ ] 5.2 Add `container-type: inline-size` to parent containers that are missing it
- [ ] 5.3 Convert any remaining viewport-width media queries to container queries

## 6. Anchor Positioning expansion

- [ ] 6.1 Identify tooltip and dropdown components that use JS positioning
- [ ] 6.2 Replace JS positioning with CSS Anchor Positioning (`position-anchor`, `position-area`, `position-try-fallbacks`)
- [ ] 6.3 Add `@supports` fallback for browsers without Anchor Positioning support

## 7. Verification

- [ ] 7.1 Run `make check` — zero stylelint errors, zero biome errors
- [ ] 7.2 Run `make test` — all unit tests pass
- [ ] 7.3 Grep for remaining JS scroll listeners used for visual effects — zero matches
- [ ] 7.4 Grep for `requestAnimationFrame` used for entry animation — zero matches
- [ ] 7.5 Grep for viewport-width `@media` queries in component CSS — zero matches
