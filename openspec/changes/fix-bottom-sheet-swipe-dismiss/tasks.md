## 1. Markup & structure (bottom-sheet.html)

- [ ] 1.1 Replace the inner `<dialog>` host with a `popover="manual"` element (via `ref`); set `role="dialog"`, `aria-modal="true"`, and mirror the accessible name (`aria-label`/`aria-labelledby`) onto it
- [ ] 1.2 Keep the internal DOM `[popover] > .scroll-area > .dismiss-zone + section.sheet-body`; make the sheet body focusable (`tabindex="-1"`) for focus-in on open
- [ ] 1.3 Remove the `cancel`/`close` `<dialog>` event bindings and the `scrollend`/`scrollsnapchange`/`pointerup` handlers from `.scroll-area`; keep the `.dismiss-zone` `click` binding

## 2. Styles (bottom-sheet.css)

- [ ] 2.1 `.scroll-area`/`.dismiss-zone`: `100dvh` → `100svh`; `overscroll-behavior-y: contain` → `overscroll-behavior: none`
- [ ] 2.2 `.sheet-body`: `max-block-size: 90dvh` → `90svh` (keep `contain: layout`, radius, shadow, background tokens)
- [ ] 2.3 Retain the `initial-snap` keyframe hack; add a code comment marking `scroll-initial-target: nearest` as the replacement to apply once it reaches Baseline (Chromium-only / not Baseline as of 2026-08)
- [ ] 2.4 Gate the dismiss scroll on `@media (prefers-reduced-motion: no-preference) { .scroll-area { scroll-behavior: smooth } }`; remove the fixed-duration `opacity`/`overlay allow-discrete` close fade that competed with the scroll
- [ ] 2.5 Keep the `@supports (animation-timeline: scroll())` scroll-timeline backdrop fade and its opacity-transition fallback, re-scoped to the popover `::backdrop`

## 3. ViewModel — lifecycle & open (bottom-sheet.ts)

- [ ] 3.1 `openChanged(true)`: call `showPopover()` (try/catch for pre-attach ref), record `document.activeElement`, apply background `inert`, move focus into the sheet body; retry in `attached()` when `this.open`
- [ ] 3.2 Add the just-opened dismiss guard: suppress dismiss signals until the sheet has settled on `.sheet-body`; release the guard on settle
- [ ] 3.3 `openChanged(false)` (programmatic close): initiate the scroll-to-closed-stop dismiss (shared close path), not an immediate `hidePopover()`

## 4. ViewModel — dismiss via IntersectionObserver

- [ ] 4.1 Create an `IntersectionObserver` on `.sheet-body` (root = popover) as the single source of truth; on the body leaving the viewport (and past the just-opened guard): remove background `inert`, call `hidePopover()`, set `open = false`, dispatch `sheet-closed` (`bubbles: true`)
- [ ] 4.2 Implement the shared `dismiss()` = scroll `.scroll-area` to the closed snap stop (dismiss zone); lift background `inert` as soon as the dismiss scroll begins so the closing window is interactive
- [ ] 4.3 Wire dismiss triggers to `dismiss()`: `.dismiss-zone` click (only when `dismissable`), Escape `keydown` (only when `dismissable`), programmatic `open=false`
- [ ] 4.4 Remove the `onSnapChange`/`onScrollEnd`/`onPointerUp` heuristics and the `pointer-events: none` bounce-back lock entirely

## 5. ViewModel — non-dismissable & a11y

- [ ] 5.1 `dismissable=false`: keep background `inert` for the whole lifetime; suppress the Escape handler and the `.dismiss-zone` click; set `data-dismissable="false"` (CSS already disables dismiss-zone snap)
- [ ] 5.2 Add a lightweight focus trap (wrap Tab within the sheet) since `popover` does not trap; restore focus to the previously-focused element on close
- [ ] 5.3 `detaching()`: disconnect the `IntersectionObserver`, remove the Escape `keydown` and `.dismiss-zone` click listeners, remove any CE-applied `inert`, and call `hidePopover()`

## 6. Tests

- [ ] 6.1 Update `bottom-sheet.spec.ts`: open/close via bindable (showPopover/hidePopover), `sheet-closed` on each path, non-dismissable suppresses ESC/tap-outside, focus move+restore, detach cleanup (observer disconnected, inert removed)
- [ ] 6.2 Add/extend E2E: swipe-down dismiss closes; reverse-mid-gesture keeps it open with no bounce-back; tap another concert card during the close animation opens the new sheet (operation-lock regression); keyboard Escape dismiss
- [ ] 6.3 Confirm the artist-filter chip-check E2E (`contain: layout` stability) still passes

## 7. Verify & consumer smoke

- [ ] 7.1 Run `make check` (Biome lint + stylelint + typecheck + vitest) and `npx playwright test` for the affected suites
- [ ] 7.2 Smoke all `<bottom-sheet>` consumers (event-detail-sheet, post-signup-dialog, date-range-sheet, artist-unfollow-sheet, user-home-selector, page-help): open/close, dismissable vs non-dismissable, focus behavior
- [ ] 7.3 Verify on iOS Safari (no height jump on address-bar resize during swipe) and Firefox (backdrop-fade fallback + IO dismiss)

## 8. Ship & spec sync

- [ ] 8.1 Open the frontend PR (Refs the tracking issue), pass CI, merge, and ship to prod via the frontend release
- [ ] 8.2 At archive/sync time, update the `bottom-sheet-ce` main-spec `## Purpose` line to describe the `popover` architecture (the delta does not carry Purpose)
