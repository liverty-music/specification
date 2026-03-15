## 1. event-detail-sheet: CSS scroll snap dismiss

- [x] 1.1 Remove `overflow-y: auto` from `.sheet-body` in `event-detail-sheet.css`; adjust `max-block-size` to `max-content` or remove it
- [x] 1.2 Add a scroll snap wrapper element in `event-detail-sheet.html`: wrap `.sheet-body` in a container with `scroll-snap-type: y mandatory` and `overscroll-behavior: contain`
- [x] 1.3 Add a `.dismiss-zone` element after `.sheet-body` with `scroll-snap-align: end` and appropriate `block-size` (e.g., `30vh`)
- [x] 1.4 Set `scroll-snap-align: start` on `.sheet-body`
- [x] 1.5 In `event-detail-sheet.ts`: remove `onTouchStart`, `onTouchMove`, `onTouchEnd` methods and associated properties (`touchStartY`, `isDragging`, `dragOffset`, `DISMISS_THRESHOLD`)
- [x] 1.6 In `event-detail-sheet.ts`: add `scrollend` event handler on the scroll snap wrapper that calls `close()` when `scrollTop > threshold`
- [x] 1.7 In `event-detail-sheet.html`: remove `touchstart.trigger`, `touchmove.trigger`, `touchend.trigger` bindings and `drag-offset.bind`
- [x] 1.8 Handle non-dismissable mode: when `isDismissable` is false (onboarding Step 4), hide or disable the dismiss-zone (e.g., `display: none` on dismiss-zone, `scroll-snap-type: none` on wrapper)
- [ ] 1.9 Ensure snap-back animation feels native: verify scroll snap momentum and deceleration are smooth on mobile

## 2. Dead custom attribute cleanup

- [x] 2.1 Delete `src/custom-attributes/drag-offset.ts`
- [x] 2.2 Delete `src/custom-attributes/swipe-offset.ts` (orphaned, zero HTML usage)
- [x] 2.3 Remove `DragOffsetCustomAttribute` and `SwipeOffsetCustomAttribute` imports and registrations from `main.ts`
- [x] 2.4 Remove CSS `--_drag-y` and `translate: 0 var(--_drag-y, 0)` from `event-detail-sheet.css`

## 3. @starting-style audit — already compliant

- [x] 3.1 Verify all popover/toast entry animations already use `@starting-style` (confirmed for: event-detail-sheet, toast-notification, discover-page, my-artists-page, user-home-selector)
- [x] 3.2 Confirm no `requestAnimationFrame` is used for entry animation deferrals (coach-mark's rAF is for top-layer re-insertion, dna-orb's rAF is for Canvas render loop — both are correct non-animation usage)
- [x] 3.3 Already compliant — no gaps found

## 4. CSS :has() audit — no candidates found

- [x] 4.1 Audit parent-state styling patterns: check if any TS code toggles a class or attribute on a parent element based on child state
- [x] 4.2 Confirm current `data-active` usage is on the elements themselves (child), not set on parents by TS — no `:has()` conversion needed
- [x] 4.3 Confirm `data-search-mode` on discover-page is driven by programmatic TS state (not child DOM state) — `:has()` not applicable
- [x] 4.4 No candidates found

## 5. Scroll-driven Animations audit — no candidates

- [x] 5.1 Check for JS `addEventListener('scroll', ...)` used for visual effects — confirmed none exist (coach-mark's `scrollend` listener is for scroll-into-view completion, not visual effects)
- [x] 5.2 Evaluate sticky headers (my-artists-page hype-legend, live-highway date-separator) for scroll-driven shadow animation — no shadow design exists for these headers
- [x] 5.3 No candidates — sticky headers have no shadow-on-scroll design

## 6. Container Queries audit — already compliant

- [x] 6.1 Confirm no viewport-based `@media (min-width)` or `@media (max-width)` queries exist in component CSS (confirmed: zero matches)
- [x] 6.2 Already compliant

## 7. Verification

- [x] 7.1 Run `make check` — stylelint warnings only in pre-existing files (error-banner, discover-page), zero errors in changed files
- [x] 7.2 Run `make test` — all 588 unit tests pass
- [x] 7.3 Grep: no references to deleted custom attributes (`drag-offset`, `swipe-offset`, `DragOffsetCustomAttribute`, `SwipeOffsetCustomAttribute`) — confirmed zero matches
- [x] 7.4 Grep: no JS `touchstart`/`touchmove`/`touchend` handlers in event-detail-sheet — confirmed zero matches
- [ ] 7.5 Manual test: swipe-to-dismiss works on mobile with native scroll feel
- [ ] 7.6 Manual test: non-dismissable mode (onboarding) blocks swipe dismiss
