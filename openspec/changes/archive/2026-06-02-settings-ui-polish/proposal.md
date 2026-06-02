## Why

A multi-lens `/code-review` of the Settings page (cube-css / web-design-specialist / modern-web-guidance / aurelia-specialist) during the `introduce-entity-store-layer` work surfaced a cluster of pre-existing UI debt: accessibility gaps in the shared bottom-sheet and the selectors, CUBE CSS layer drift, and two correctness/altitude issues. The store-driven reactivity itself was verified clean — these are not regressions from the store refactor.

Investigation while triaging the bottom-sheet a11y gap (#1) revealed a deeper, two-part regression and a spec/implementation inconsistency:

- The shared `<bottom-sheet>` is a `popover="auto"` host with a manually-set `role="dialog"`. It does **not** trap focus or `inert` the background, so keyboard/SR users can Tab out into the still-interactive page behind an open sheet. Earlier area-selection sheets (archived `fix-area-dialog-overlap`) deliberately used `<dialog>.showModal()` *for* focus-trap + `::backdrop` + ESC, and the concert detail sheet (archived `fix-detail-sheet-dismiss`) added tap-outside dismiss. **Both behaviors were lost when those surfaces were consolidated onto the popover-based shared CE.**
- The `settings` capability spec already requires the home-area selector to be a native `<dialog>` opened via `showModal()` with backdrop/ESC dismiss, but the implementation drifted to the popover-based shared `<bottom-sheet>`. Spec and code are inconsistent today.
- The swipe-down dismiss feels sluggish: dismiss is gated on `scrollend` (native scroll-snap settle, UA-controlled and floaty) followed by a 300ms exit transition that only *starts* after the gesture settles. The backdrop blur stays fully applied throughout the swipe and fades only afterward, so it reads as disconnected from the finger. A scroll-driven backdrop fade existed (`8d905f3`) but was dropped as collateral of the popover→CE-host refactor (`72c768a`/`b362a95`), not because it was wrong.

Doing the bottom-sheet a11y fix (#1) and the UX polish together restores focus-trap, tap-outside, and the gesture-coupled backdrop in one structural change, and reconciles the `settings` spec with reality.

## What Changes

**Shared bottom-sheet (highest leverage — touches home selector, language selector, and other surfaces):**
- Migrate the shared `<bottom-sheet>` from a `popover="auto"` host to a native `<dialog>.showModal()` (CE host wraps an inner `<dialog>`), restoring focus-trap + `inert` + ESC + Android back (close request) for free.
- Preserve the full-viewport scroll-snap geometry that powers swipe-down dismiss (host-agnostic — the scroll mechanism lives on an internal scroll container, not the host).
- Add tap-outside dismiss via a `click` handler on the existing `.dismiss-zone` div (NOT `::backdrop` — UA forces `pointer-events: none` there; NOT `closedby` — Safari-unsupported and never fires under full-viewport coverage).
- Restore a scroll-driven backdrop fade so the blur tracks the swipe and is gone by the dismiss threshold, gated behind `@supports (animation-timeline: scroll())` with the current transition as the fallback.
- Make swipe dismiss feel responsive by firing close on the snap-change/threshold rather than waiting for full `scrollend` settle, and shorten the exit transition; preserve the `prefers-reduced-motion` instant path.

**A. Accessibility / semantics (Settings):**
- Language selector becomes a single-select control (`role="radiogroup"`/`role="radio"` + `aria-checked`) instead of a list of `data-selected` buttons.
- Home-area selector shows a reactive selected-state indicator (bind `aria-checked`/`data-selected` off the now-observable `userStore.currentHome`).
- Async state changes announced via a polite live region (resend-verification button text, verified/not-verified badge).
- Toggle hint text associated via `aria-describedby`; the VAPID-unavailable push row uses `aria-disabled` + explanation instead of native `disabled` (which removes it from AT discovery).
- Settings groups gain list semantics (`role="list"`/`<ul><li>`), dropping the `<hr>` separator noise.
- Email + verification badge programmatically associated; badge gains a non-color status cue.

**B. CUBE CSS:**
- Move `data-*` state hooks (`data-on`/`data-selected`/`data-disabled`/`data-verified`) into the declared-but-unused `@layer exception`.
- Extract duplicated toggle geometry/duration into `--toggle-*` / `--duration-*` tokens (currently hard-coded byte-for-byte in both `settings-route.css` and `consent-route.css`).
- Apply bracket grouping (`[ block ] [ composition ] [ utilities ]`) consistently.
- NOTE: the original #8 finding (`.settings-row` re-implementing flex clusters, `.settings-volume-row` double-applied) is **largely obsolete** — the `align rows via card-grid + row-subgrid` refactor (#409, merged after the issue was filed) already moved rows to subgrid. This change re-scopes B to the still-valid `@layer exception` + token-extraction work and drops the stale parts.

**C. Correctness / altitude:**
- `selectLanguage` closes the sheet *after* success (and surfaces the non-`ConnectError` failure class) instead of closing before the guard + `await`.
- Consent toggles bind the consent state directly: make `ConsentService` expose `@observable` state and delete the component-local `analyticsConsent`/`marketingConsent` mirrors + write-back handlers (and the fabricated "RC1 won't re-evaluate a getter" doc-comment). Removes a mirror-drift risk and makes consent consistent with the observable UserStore/GuestService owners.

## Capabilities

### New Capabilities
<!-- None — all changes modify existing capabilities. -->

### Modified Capabilities
- `bottom-sheet-ce`: dialog primitive changes from Popover API host to native `<dialog>.showModal()`; adds focus-trap/`inert`, tap-outside (via `.dismiss-zone`), gesture-coupled scroll-driven backdrop fade, and responsive (snap-change/threshold) dismiss; ESC/Android back via close request. Reconciles with the `settings` spec's existing `<dialog>`/`showModal()` requirement.
- `settings`: language selector single-select (radiogroup) semantics; home-area selected-state indicator; async live-region announcements; toggle-hint association + `aria-disabled` push row; settings-group list semantics; email/badge association + non-color cue; `selectLanguage` close-after-success + error surfacing; consent toggles bound to observable consent state (no component-local mirror).

## Impact

- **Frontend code**: `src/components/bottom-sheet/` (host → `<dialog>`, scroll-driven backdrop, dismiss timing), `src/routes/settings/` (template a11y, CSS layer/token cleanup, `selectLanguage`, consent binding), `src/components/user-home-selector/` (selected-state), `src/lib/consent/consent-service.ts` (`@observable` state), `src/routes/consent/consent-route.css` (shared toggle tokens).
- **Other bottom-sheet consumers** (verify non-breaking under `showModal()`): language selector, `user-home-selector`, `post-signup-dialog`, onboarding `page-help`, onboarding spotlight top-layer coordination (LIFO ordering with the coach-mark popover — see archived `fix-detail-sheet-dismiss`).
- **Spikes required before implementation**: (1) CE host wrapping an inner `<dialog>` is non-breaking across all consumers; (2) `<dialog>.showModal()` fires `cancel` on Android back (close request); (3) the `contain: layout` Chromium scroll-snap workaround still holds under dialog top-layer (regression guard: artist-filter chip-check E2E).
- **Browser support**: `<dialog>`/`showModal()`/`::backdrop` are Baseline widely available; scroll-driven backdrop is Chrome 115+/Safari 26+/not-Firefox → `@supports` gate + transition fallback.
- **Testing/CI**: DOM-shape changes (radiogroup, `<dialog>`, list semantics) will shift visual baselines — baseline regeneration is required before merge (frontend visual baselines are a main-branch CI artifact with no PR update path).
- Tracked by frontend#399. Goal includes shipping through dev to prod, not stopping at merge.
