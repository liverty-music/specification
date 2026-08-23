## 1. Markup & structure (bottom-sheet.html)

- [x] 1.1 Replace the inner `<dialog>` host with a `popover="manual"` element (via `ref`); set `role="dialog"`, `aria-modal="true"`, and mirror the accessible name (`aria-label`/`aria-labelledby`) onto it — implemented as `<dialog popover="manual">` (repo lint rule `lint-no-div-popover` mandates `<dialog>`, which also supplies the native dialog role)
- [x] 1.2 Keep the internal DOM `[popover] > .scroll-area > .dismiss-zone + section.sheet-body`; make the sheet body focusable (`tabindex="-1"`) for focus-in on open
- [x] 1.3 Remove the `cancel`/`close` `<dialog>` event bindings and the `scrollsnapchange` handler from `.scroll-area`; keep the `.dismiss-zone` `click` binding

## 2. Styles (bottom-sheet.css)

- [x] 2.1 `.scroll-area`/`.dismiss-zone`: `100dvh` → `100svh`; `overscroll-behavior-y: contain` → `overscroll-behavior: none`
- [x] 2.2 `.sheet-body`: `max-block-size: 90dvh` → `90svh` (keep `contain: layout`, radius, shadow, background tokens)
- [x] 2.3 Retain the `initial-snap` keyframe hack; add a code comment marking `scroll-initial-target: nearest` as the replacement to apply once it reaches Baseline (Chromium-only / not Baseline as of 2026-08)
- [x] 2.4 Gate the dismiss scroll on `@media (prefers-reduced-motion: no-preference) { .scroll-area { scroll-behavior: smooth } }`; remove the fixed-duration `opacity`/`overlay allow-discrete` close fade that competed with the scroll
- [x] 2.5 Keep the `@supports (animation-timeline: scroll())` scroll-timeline backdrop fade and its opacity-transition fallback, re-scoped to the popover `::backdrop`

## 3. ViewModel — lifecycle & open (bottom-sheet.ts)

- [x] 3.1 `openChanged(true)`: call `showPopover()` (try/catch for pre-attach ref), record `document.activeElement`, apply background `inert`, move focus into the sheet body; retry in `attached()` when `this.open`
- [x] 3.2 Add the just-opened dismiss guard: suppress dismiss signals until the sheet has settled on `.sheet-body`; release the guard on settle
- [x] 3.3 `openChanged(false)` (programmatic close): initiate the scroll-to-closed-stop dismiss (shared close path), not an immediate `hidePopover()`

## 4. ViewModel — dismiss via IntersectionObserver

- [x] 4.1 Create an `IntersectionObserver` on `.sheet-body` as the single source of truth; on the body leaving the viewport (and past the just-opened guard): remove background `inert`, call `hidePopover()`, set `open = false`, dispatch `sheet-closed` (`bubbles: true`)
- [x] 4.2 Implement the shared `startDismiss()` = scroll `.scroll-area` to the closed snap stop (dismiss zone); lift background `inert` as soon as the dismiss scroll begins so the closing window is interactive
- [x] 4.3 Wire dismiss triggers to `startDismiss()`: `.dismiss-zone` click (only when `dismissable`), Escape `keydown` (only when `dismissable`), programmatic `open=false`
- [x] 4.4 Remove the `onSnapChange`/`onScrollEnd`/`onPointerUp` heuristics and the `pointer-events: none` bounce-back lock entirely

## 5. ViewModel — non-dismissable & a11y

- [x] 5.1 `dismissable=false`: keep background `inert` for the whole lifetime; suppress the Escape handler and the `.dismiss-zone` click; set `data-dismissable="false"` (CSS already disables dismiss-zone snap)
- [x] 5.2 Add a lightweight focus trap (wrap Tab within the sheet) since `popover` does not trap; restore focus to the previously-focused element on close
- [x] 5.3 `detaching()`: disconnect the `IntersectionObserver`, remove the Escape `keydown` and `.dismiss-zone` click listeners, remove any CE-applied `inert`, and call `hidePopover()`

## 6. Tests

- [x] 6.1 Update `bottom-sheet.spec.ts` (unit) + `test/components/bottom-sheet.spec.ts` (Layer 2): open/close via bindable (showPopover/hidePopover), `sheet-closed` per path, programmatic vs user emit, just-opened guard, reverse-no-bounce-back, non-dismissable suppresses ESC/tap-outside, detach cleanup — 28 tests pass
- [x] 6.2 E2E regression guards: updated `page-help-sheet-webkit.spec.ts` (WebKit flash-then-close → `:popover-open`) and `detail-sheet-dismiss.spec.ts` (popover-aware, back-button dismiss passes). NOTE: the interactive swipe/tap device-gesture E2E stay `test.fixme` (headless Chromium cannot drive scroll-snap smooth-scroll/scrollend reliably); reverse-no-bounce-back is covered by unit tests
- [x] 6.3 Confirm the artist-filter chip-check E2E (`contain: layout` stability) still passes — green in CI

## 7. Verify & consumer smoke

- [x] 7.1 CI `make check` (Biome lint + stylelint + typecheck + vitest) and Playwright E2E all green on PR #559
- [x] 7.2 Consumer contract verified at code/test level: `event-detail-sheet` unit tests pass and the public CE contract (`open`/`dismissable`/`sheet-closed`) is unchanged, so consumers need no changes. NOTE: per-consumer interactive device smoke deferred — dev env intentionally stopped
- [x] 7.3 Automated WebKit regression guard (`page-help-sheet-webkit`, real WebKit) covers the iOS flash-then-close path. NOTE: interactive iOS Safari (address-bar `svh` stability) and Firefox (backdrop-fade fallback) confirmation deferred to a real-device check by the user — dev env stopped, no emulator path

## 8. Ship & spec sync

- [x] 8.1 Frontend PR #559 opened (Refs specification#837), CI green, merged; shipped to prod via Release v1.58.0 — fan-web prod pin bumped (recovery dispatch after the concurrency race dropped it) and ArgoCD rolled out `fan-web:v1.58.0` (verified running in prod)
- [x] 8.2 Update the `bottom-sheet-ce` main-spec `## Purpose` line to describe the `popover` architecture (done in this archive sync)
