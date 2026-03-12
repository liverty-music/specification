## 1. Coach Mark — Anchored Container Query + `scrollIntoView`

- [x] 1.1 Add `container-type: anchored` to `.coach-mark-tooltip` in `coach-mark.css`
- [x] 1.2 Update `.coach-mark-tooltip` to use `position-try-fallbacks: flip-block` (built-in keyword, auto-flips `position-area` and `margin-block`)
- [x] 1.3 Add `@container anchored(fallback: flip-block)` rule to toggle `.coach-arrow-above` / `.coach-arrow-below` visibility
- [x] 1.4 Fix `display:none → block` animation issue: apply final SVG state (`stroke-dashoffset: 0`, `opacity: 1`) inside `@container anchored` for the revealed arrow
- [x] 1.5 Remove custom `@position-try --flip-to-top` rule (replaced by built-in `flip-block`)
- [x] 1.6 Correct SVG arrow paths: `.coach-arrow-above` points up (to target above), `.coach-arrow-below` points down (to target below)
- [x] 1.7 Remove `flipped` property, `tooltipEl` ref, and `detectFlip()` method from `coach-mark.ts`
- [x] 1.8 Remove `ref="tooltipEl"` and `data-flipped="${flipped}"` from `coach-mark.html`
- [x] 1.9 Remove `isInViewport()` and `getBoundingClientRect()` from `coach-mark.ts`
- [x] 1.10 Add `smoothScrollTo()` method: `scrollIntoView({ behavior: 'smooth', block: 'center' })` + `scrollend` event + 800ms failsafe timeout
- [x] 1.11 Make `highlight()` async: call `smoothScrollTo()` before anchor-name assignment and `showPopover()`
- [x] 1.12 Remove `rAF` wrapper around `showPopover()` — call directly after scroll settles
- [x] 1.13 Update unit tests: remove `rAF` mocking, add `scrollIntoView` assertion, add `scrollend` event test, advance past failsafe timeout

## 2. Toast Notification — `@starting-style` + `transitionend`

- [x] 2.1 Remove `requestAnimationFrame` from toast creation — set `visible: true` immediately
- [x] 2.2 Add `@starting-style` to `toast-notification.css` with `opacity: 0` and `translateY(-1rem)` for entry animation
- [x] 2.3 Add `data-state` attribute binding (`entering`/`exiting`) to toast element in `toast-notification.html`
- [x] 2.4 Add `.toast-item[data-state="exiting"]` CSS rule with `opacity: 0` and `translateY(-1rem)`
- [x] 2.5 Remove inline Tailwind animation classes from toast template — use `.toast-item` class with CSS-driven transitions
- [x] 2.6 Replace `setTimeout(400)` DOM cleanup with `transitionend` listener on host element via `resolve(INode)`
- [x] 2.7 Add `attached()` lifecycle to register `transitionend` listener, `detaching()` to remove it
- [x] 2.8 Implement `onTransitionEnd()`: match `propertyName === 'opacity'` + `dataset.toastId`, remove toast from array, call `hidePopover()` when last toast removed
- [x] 2.9 Add `@media (prefers-reduced-motion: reduce)` rule with `transition: none`
- [x] 2.10 Update unit tests: remove `rAF` mocking, polyfill `TransitionEvent` for jsdom, test `transitionend`-based removal

## 3. Event Detail Sheet — `overscroll-behavior: contain`

- [x] 3.1 Add `overscroll-behavior: contain` to `.event-detail-sheet .overflow-y-auto` in `event-detail-sheet.css`

## 4. Celebration Overlay — `transitionend` for fade-out

- [x] 4.1 Replace `setTimeout(400)` in `startFadeOut()` with `transitionend` listener via `resolve(INode)`
- [x] 4.2 Add `attached()` lifecycle to register `transitionend` listener, update `detaching()` to remove it
- [x] 4.3 Implement `onTransitionEnd()`: match `propertyName === 'opacity'` + `fadingOut` state, set `visible = false`, call `onComplete()`
- [x] 4.4 Update template: replace `.fade-out` class with `data-state="${fadingOut ? 'exiting' : 'active'}"` attribute
- [x] 4.5 Update CSS: replace `.celebration-overlay.fade-out` selector with `.celebration-overlay[data-state="exiting"]`

## 5. Bug Fixes Discovered During E2E Testing

- [x] 5.1 Fix celebration overlay not rendering when `active` is true from initial binding — add `attached()` fallback to call `show()` when `activeChanged` fires during `bind()` phase before template is ready

## 6. Validation

- [x] 6.1 Run `make check` — all lint (Biome, Stylelint, TypeScript) and unit tests pass (378/378)
- [x] 6.2 Run Playwright E2E layout tests — 30/37 pass (7 pre-existing failures in dashboard/discover layout, unrelated)
- [x] 6.3 E2E: celebration overlay completes via `transitionend`, uses `data-state` attribute, and is removed from DOM (`e2e/css-antipattern-verification.spec.ts`)
- [x] 6.4 Playwright verification: coach mark arrow renders correctly when tooltip flips above bottom-nav via `@container anchored(fallback: flip-block)` — `strokeDashoffset: 0`, `opacity: 1`, `display: block`
- [x] 6.5 Playwright verification: toast notification CSS uses `@starting-style`, `transitionend` listener, `data-state` attribute, and `prefers-reduced-motion` rule
- [x] 6.6 Playwright verification: event detail sheet has `overscroll-behavior: contain` on `.overflow-y-auto`
- [x] 6.7 E2E: reduced motion bypasses `transitionend` — celebration overlay removed immediately without fade transition (`e2e/css-antipattern-verification.spec.ts`)
