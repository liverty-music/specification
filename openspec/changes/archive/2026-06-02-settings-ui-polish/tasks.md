## 1. Spikes (gate — resolve before implementation)

- [x] 1.1 Spike: prove the CE host (`<bottom-sheet>`) can wrap an inner `<dialog ref>` opened via `showModal()` without breaking any consumer (language selector, `user-home-selector`, `post-signup-dialog`, onboarding `page-help`). FINDING: 11 consumer surfaces; the bindable contract (`open`/`dismissable`/`sheet-closed`/`aria-label`) must be preserved verbatim. Non-dismissable consumers (`error-banner`, tickets-generating) depend on suppress-dismiss; `event-detail-sheet` adds its own `popstate`/`pushState` history handling on top of the sheet.
- [x] 1.2 Spike: `<dialog>.showModal()` fires `cancel` on Android back — CONFIRMED on-device; no CloseWatcher shim needed.
- [x] 1.3 Spike: `contain: layout` workaround holds under `<dialog>` top-layer — CONFIRMED (artist-filter chip-check E2E green in PR #410 and #415 CI).
- [x] 1.4 Spike: audit onboarding spotlight top-layer coordination against a modal `<dialog>` sheet. FINDING (verified against current code, NOT the stale archived `fix-detail-sheet-dismiss` doc): the global `coach-mark` (app-shell) and any `<bottom-sheet>` do NOT coexist in current flows — `activateSpotlight()` is called only in `discovery-route` targeting `[data-nav="home"]` (no sheet open), and `event-detail-sheet` is opened by `dashboard-route` (no spotlight). `bringSpotlightToFront()`/`onBringToFront` is dead code (no caller). So `showModal()`'s `inert` does NOT break onboarding today. RESIDUAL NOTE: if a future onboarding step layers the coach-mark over a now-modal sheet, the inert conflict would bite — document the constraint and delete the dead `bringSpotlightToFront` plumbing.

## 2. PR-1 — Shared bottom-sheet migration to `<dialog>.showModal()`

- [x] 2.1 Restructure `bottom-sheet.html` so the CE host wraps an inner `<dialog ref>`; move `.scroll-area > .dismiss-zone + section.sheet-body` inside it
- [x] 2.2 Swap `showPopover()`/`hidePopover()` → `showModal()`/`close()` in `bottom-sheet.ts`; replace the `toggle` listener with `cancel`/`close` handlers; keep the pre-attach retry + detach cleanup
- [x] 2.3 Move `popover`/`:popover-open` CSS to `<dialog>` equivalents (`[open]`, `dialog::backdrop`); keep `@starting-style` + `transition: overlay allow-discrete` on the `<dialog>`
- [x] 2.4 Add tap-outside: `click.trigger` on `.dismiss-zone` (`onDismissZoneClick`), gated by `dismissable`
- [x] 2.5 Make swipe dismiss responsive: fire close on `scrollsnapchange` (snap target = dismiss zone) instead of waiting for full `scrollend` settle; `onScrollEnd` kept as fallback. CODE COMPLETE — live snap timing needs runtime verify.
- [x] 2.6 Restore scroll-driven backdrop fade via `animation-timeline: scroll()` inside `@supports (animation-timeline: scroll())`; keep the opacity `transition` as the Firefox fallback; tokenize (`--_duration`) + shorten (300ms→240ms). CODE COMPLETE — visual fade needs runtime verify.
- [x] 2.7 Non-dismissable mode: `preventDefault()` the `cancel` event so ESC / Android back do not close; preserve dismiss-zone `pointer-events: none`
- [x] 2.8 `prefers-reduced-motion` retargeted to `.sheet-dialog`; scroll-driven fade is scroll-position-based (inherently no time-motion). CSS COMPLETE — visual needs runtime verify.
- [x] 2.9 Rewrote both unit specs to the dialog API (25 tests); full suite green (106 files / 1187 tests) → no consumer regression. Focus-trap/ESC/Android live behavior = runtime (jsdom lacks `showModal`).
- [x] 2.10 `bottom-sheet-ce` spec scenarios satisfied; the `settings` spec's `<dialog>`/`showModal()` home-selector requirement is now structurally met by the shared CE. `make lint` + `tsc` green.
- [x] 2.11 RUNTIME MERGE-GATE: verified focus-trap + inert + radiogroup (browser a11y tree: `dialog … modal: true`), ESC + Android back close (on-device), tap-outside, `contain: layout` stability (chip-check E2E green). Scroll-driven backdrop shipped. Dead `bringSpotlightToFront`/`onBringToFront` plumbing removed in PR #415 (merged `e27ab4e`).

## 3. PR-2 — Settings accessibility / semantics

- [x] 3.1 Language selector → `role="radiogroup"` + `role="radio"` + `aria-checked` (visual check icon + `data-selected` retained for styling only)
- [x] 3.2 Home-area selector → `data-selected`/`aria-current` bound off observable `userStore.currentHome` (`currentHomeCode` getter); `codeToHome(code).level1 === code` confirms format match for authed + guest
- [x] 3.3 Verification badge is an `<output aria-live="polite">`; resend button is `aria-live="polite"` so its label transitions announce
- [x] 3.4 Toggle hints associated via `aria-describedby` (`push-na-hint` / `sound-ios-hint`); push row switched to `aria-disabled` + `toggleNotifications` guard (not native `disabled`)
- [x] 3.5 Cards are `<ul role="list">` + `<li class="settings-list-item">` (display:contents, subgrid preserved); `<hr>`s dropped, dividers now CSS row borders
- [x] 3.6 Email associated with badge via `aria-describedby`; badge carries a non-color status icon (check / alert-triangle)
- [x] 3.7 VM unit tests unaffected (full suite 1189 green); DOM/visual snapshot regen is the runtime baseline gate

## 4. PR-3 — CUBE CSS cleanup

- [x] 4.1 DESCOPED (not implemented): moving state hooks to `@layer exception` is blocked by `cube/data-attr-naming` (exception layer permits only `data-state`/`data-variant`/`data-theme`) + the `no-ternary`/`no-data-interpolation` template rules → needs a separate `data-state` vocabulary migration. NOT a spec requirement (no spec delta depends on it); state hooks stay valid flat `data-*` rules in `@layer block`. Removed from this change's scope; capture as a standalone follow-up if pursued.
- [x] 4.2 Extracted `--toggle-*` geometry tokens (tokens.css) + reused existing `--transition-*` durations; de-duplicated the toggle track/thumb values in `settings-route.css` and `consent-route.css`
- [x] 4.3 DESCOPED (not implemented): single-class `<li>`s + the bracketed volume row already group correctly; a full bracket sweep of the remaining two-block-class rows is a low-value cosmetic follow-up with no lint rule enforcing it. Removed from this change's scope.
- [x] 4.4 `make lint` green (biome + stylelint + tsc + cube-css rules + brand-vocab); production build green; no intended behavior change (visual baseline regen at runtime gate)

## 5. PR-4 — Correctness / altitude

- [x] 5.1 `selectLanguage`: close the sheet after success (and on the no-op path); on a non-`ConnectError` rethrow keep the sheet OPEN so the failure is not masked as a successful dismissal; close + Snack on ConnectError. Test updated.
- [x] 5.2 `ConsentService`: `@observable private state` (immutable reassignment unchanged); `grant`/`revoke` still publish `ConsentChanged`
- [x] 5.3 Settings VM: `consent` made public; template binds `consent.analytics` / `consent.marketingMeasurement` directly; deleted `analyticsConsent`/`marketingConsent` mirrors + write-back + the fabricated RC1 doc-comment; handlers write through to the service
- [x] 5.4 Added tests: external consent change reflected with no mirror; `handleAnalyticsToggle` writes through. 63 affected tests green.

## 6. Validation, baselines, and release

- [x] 6.1 `make lint` + full unit suite green (PR #410 and #415 CI).
- [x] 6.2 E2E (Playwright) green in CI (bottom-sheet + settings flows; chip-check guard).
- [x] 6.3 Visual baselines regenerated (deleted stale artifacts → main CI regenerated on merge of #410).
- [x] 6.4 Merged: #410 (impl, `edb3c88`) + #415 (dead-code cleanup, `e27ab4e`).
- [x] 6.5 dev verify N/A — dev env intentionally stopped; verified locally (browser a11y tree) instead.
- [x] 6.6 Shipped to prod: release **v1.5.2** → prod AR retag → pin-bump (`bd17ba8`) → ArgoCD synced; prod `web-app` on v1.5.2, 1/1 Healthy.
- [x] 6.7 Archive this OpenSpec change (this step).
