## Context

The shared `<bottom-sheet>` custom element is the single dialog primitive for all overlay content (`bottom-sheet-ce` spec). Today it is a `popover="auto"` host with a manually-set `role="dialog"`, a full-viewport transparent layer (`position: fixed; inset: 0`) whose internal `.scroll-area` (`100dvh`, `scroll-snap-type: y mandatory`) provides swipe-down dismiss via a `.dismiss-zone` snap target. Closing is gated on `scrollend` → `scrollRatio < 0.1` → `hidePopover()`.

This design is the product of several prior iterations, whose lessons constrain the solution space:

- `2026-02-23 fix-area-dialog-overlap` — area sheets used `<dialog>.showModal()` *because* Popover "doesn't trap focus or provide `::backdrop`". Tap-outside was implemented via `event.target === dialog`.
- `2026-03-12 fix-detail-sheet-dismiss` — the partial-coverage detail sheet moved to `popover="auto"` for free light-dismiss + Android back (CloseWatcher), after discovering the UA rule `[popover]::backdrop { pointer-events: none !important }` makes manual `::backdrop` click dead code.
- `8d905f3` introduced a scroll-driven backdrop fade (`scroll-timeline` → `::backdrop` opacity); `72c768a` (move popover to CE host) removed the timeline consumer as collateral; `b362a95` swept the now-dead declaration and added the `contain: layout` Chromium scroll-snap-in-top-layer workaround.

Two regressions resulted from consolidating those surfaces onto the popover-based shared CE: **focus-trap/`inert` was lost** (the area-sheet behavior) and **tap-outside was lost** (the detail-sheet behavior, which relied on partial coverage exposing the backdrop — the full-viewport shared CE has no exposed backdrop). Separately, the `settings` spec still requires the home-area selector to be a `<dialog>` via `showModal()`, so spec and implementation are inconsistent.

## Goals / Non-Goals

**Goals:**
- Restore focus-trap + `inert` to the shared bottom-sheet (close the #1 a11y gap and the `settings`-spec inconsistency) via native `<dialog>.showModal()`.
- Keep the full-viewport scroll-snap swipe-down dismiss (the primary mobile gesture) intact.
- Restore tap-outside dismiss and a gesture-coupled (scroll-driven) backdrop fade.
- Make swipe dismiss feel responsive (cut the `scrollend`-settle + post-settle-transition latency).
- Land the Settings a11y, CUBE-layer, and correctness cleanups from #399 A/B/C.

**Non-Goals:**
- Reverting to a partial-height bottom sheet (would re-enable native `closedby` light-dismiss but break the scroll-snap swipe — see Decision 2).
- A JS pointer-driven drag implementation of swipe (the project deliberately moved to scroll-snap).
- Adopting `closedby="any"` (Safari-unsupported, and never fires under full-viewport coverage).
- Refactoring all CUBE CSS app-wide; scope is the settings + consent toggle surfaces and the shared toggle tokens.
- The stale #8 flex-cluster rework (already addressed by the #409 subgrid refactor).

## Decisions

### Decision 1: Native `<dialog>.showModal()` as the bottom-sheet host

**Choice**: The CE host (`<bottom-sheet>`) wraps an inner `<dialog ref>`; `open()` calls `dialog.showModal()`, `close()` calls `dialog.close()`. The `.scroll-area` / `.dismiss-zone` / `.sheet-body` structure moves inside the `<dialog>`.

**Rationale**: `showModal()` provides focus-trap, `inert` background, ESC, and Android back (close request) natively — exactly the behaviors lost in consolidation, and what the area-sheet design originally chose Popover *against*. The swipe mechanism is independent of how the host enters the top layer (confirmed by the `navigation-drawer` modern-web-guidance pattern), so it survives the host swap unchanged.

**Alternatives considered**:
- *Keep `popover="auto"` + hand-roll focus-trap + `inert`*: reimplements what `showModal()` gives free; rejected.
- *Hybrid `<dialog popover="auto">`*: a dialog opened as a popover uses `showPopover()` semantics — no focus-trap. Does not solve #1.

### Decision 2: Keep full-viewport geometry; tap-outside via `.dismiss-zone` click (not `::backdrop`, not `closedby`)

**Choice**: Add `click.trigger="close()"` to the existing `.dismiss-zone` div.

**Rationale**: Under full-viewport coverage the dialog box fills the viewport; every tap targets a dialog descendant, so native light-dismiss (popover *or* `closedby="any"`) can never fire — the dim area the user taps is the `.dismiss-zone` (dialog content), with the `::backdrop` hidden behind it. `::backdrop` itself is unusable (UA `pointer-events: none`, the documented `fix-detail-sheet-dismiss` trap). A click handler on `.dismiss-zone` is host-agnostic, works on all browsers, and converges with the swipe path (same div). This is the only minimal way to get tap-outside *while keeping swipe*.

**Trade-off (A vs B)**: Native tap-outside via `closedby` requires exposing the backdrop = a partial-height sheet (B), which removes the full-height scroll container that powers swipe. Swipe (mobile-primary) and native `closedby` (desktop convenience) require contradictory geometries. We keep swipe (A); tap-outside costs one click handler.

### Decision 3: Restore scroll-driven backdrop fade (gated), gesture-couple the dismiss

**Choice**: Re-introduce `animation-timeline: scroll()` driving `::backdrop` opacity/blur off the `.scroll-area` scroll position, inside `@supports (animation-timeline: scroll())`; keep the current opacity `transition` as the fallback. Trigger close on the snap-change/scroll-threshold (dismiss-zone becoming the snapped target) rather than waiting for full `scrollend`; shorten the exit transition and tokenize its duration. Preserve the `prefers-reduced-motion` instant path.

**Rationale**: The blur reads as "slow" because it stays fully applied through the swipe and fades only after `scrollend` over 300ms. Coupling backdrop opacity to scroll position makes the blur track the finger and be gone by the dismiss threshold. Firing close on snap-change removes the UA-controlled native-snap-settle latency (which is not CSS-tunable). This restores the `8d905f3` behavior that was dropped as refactor collateral — re-wiring the `scroll-timeline` scope correctly against the new `<dialog>` structure.

**Alternatives considered**:
- *Only shorten the exit duration*: helps the slide-out but leaves the blur decoupled from the gesture.
- *JS scroll listener writing `--backdrop` opacity*: the Firefox fallback path; acceptable but the CSS scroll-timeline is preferred where supported.

### Decision 4: Settings a11y as `settings`-capability requirements

**Choice**: Language selector → `role="radiogroup"`/`role="radio"` + `aria-checked`; home-area selected-state bound off observable `userStore.currentHome`; polite live region for async (resend/badge); `aria-describedby` for toggle hints + `aria-disabled` (not native `disabled`) for the VAPID-unavailable push row; settings groups → list semantics (drop `<hr>`); email/badge associated + non-color status cue.

**Rationale**: `semantic-dom` carries no radiogroup/live/list requirements today, and these are settings-page behaviors, so they belong in the `settings` capability. Single-select semantics + observable-driven selected-state also fix the "SR users can't tell which option is active" gap that the `data-selected` + `aria-hidden` check could not convey.

### Decision 5: Consent state becomes `@observable`; delete the component mirror

**Choice**: `ConsentService` exposes `@observable` state (immutable reassignment as today); the settings VM binds `consent.analytics` / `consent.marketingMeasurement` directly and drops `analyticsConsent`/`marketingConsent` + their write-back handlers and the fabricated RC1 doc-comment.

**Rationale**: UserStore/GuestService are already observable owners of their domains; consent is the lone component-local mirror, carrying a mirror-drift risk (an external consent change does not flow through the toggle handlers). Per `aurelia-reactivity`, getters derived from `@observable` state re-evaluate dependent bindings without a mirror.

### Decision 6: Re-scope CUBE work; no behavior delta

**Choice**: Move `data-*` state hooks into `@layer exception`; extract `--toggle-*`/`--duration-*` tokens shared by `settings-route.css` and `consent-route.css`; apply bracket grouping consistently. Drop the obsolete #8 flex-cluster rework.

**Rationale**: These are CSS-architecture changes with no observable behavior change, so they are implementation tasks under the existing `cube-css-*` specs, not spec deltas. #8's specific examples were resolved by the #409 subgrid refactor that landed after #399 was filed.

## Risks / Trade-offs

- **[Risk] CE host cannot itself be a `<dialog>`; inner-`<dialog>` wrapper changes DOM shape** → Spike first across all consumers; update the `bottom-sheet-ce` "DOM structure" scenario. The `::backdrop` and top-layer now belong to the inner `<dialog>`.
- **[Risk] Android back may not fire `cancel` as assumed** → Spike on-device / Playwright before implementation; this was the detail sheet's original reason for choosing popover.
- **[Risk] `contain: layout` Chromium workaround may behave differently under dialog top-layer** → Same top-layer class; rely on the existing artist-filter chip-check E2E regression guard; verify during spike.
- **[Resolved by spike 1.4] Onboarding spotlight vs modal `inert`**: verified against current code — the global `coach-mark` and any `<bottom-sheet>` do not coexist (`activateSpotlight()` only in `discovery-route` on `[data-nav="home"]`; `event-detail-sheet` opened by `dashboard-route` with no spotlight). `bringSpotlightToFront()`/`onBringToFront` is dead code. `showModal()`'s `inert` does not break onboarding today. Residual constraint: a future onboarding step that layers the coach-mark over a modal sheet would break (coach-mark, outside the dialog, becomes inert) — document this and delete the dead `bringSpotlightToFront` plumbing.
- **[Risk] scroll-driven backdrop unsupported in Firefox** → `@supports` gate + transition fallback (current behavior); no regression where unsupported.
- **[Trade-off] tap-outside stays a manual handler** rather than a platform freebie — accepted to preserve swipe (Decision 2).
- **[Risk] Visual baselines shift** (radiogroup, `<dialog>`, list semantics) → regenerate baselines before merge (no PR update path; main-branch CI artifact).

## Migration Plan

1. **Spikes** (gate): inner-`<dialog>` wrapper non-breaking across consumers; Android back `cancel`; `contain: layout` under dialog top-layer.
2. **PR-1 (shared bottom-sheet)**: `<dialog>.showModal()` migration + tap-outside + scroll-driven backdrop + responsive dismiss. Update `bottom-sheet-ce` spec. Verify all consumers (home/language selector, post-signup-dialog, page-help, onboarding spotlight).
3. **PR-2 (Settings a11y)**: radiogroup language selector, home-area selected-state, live regions, list semantics, badge association, toggle-hint/`aria-disabled`. Update `settings` spec.
4. **PR-3 (CUBE)**: `@layer exception` + token extraction + bracket grouping.
5. **PR-4 (correctness)**: `selectLanguage` close-after-success + consent `@observable`.
6. Regenerate visual baselines; ship through dev to prod.

Rollback: each PR is independently revertible; the bottom-sheet migration is the only structural one and is guarded by the existing E2E suite.

## Open Questions

- Does `<dialog>.showModal()` fire `cancel` on Android back across the target WebView/Chrome versions, or is a CloseWatcher shim needed? (Spike.)
- Should tap-outside on a `required`/non-dismissable sheet (onboarding home selection) stay suppressed, mirroring the current `dismissable=false` path? (Likely yes — carry the `dismissable` gate to the `.dismiss-zone` click handler.)
