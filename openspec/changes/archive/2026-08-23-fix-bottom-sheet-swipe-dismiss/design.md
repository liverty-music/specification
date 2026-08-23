## Context

See proposal.md - Why. The `<bottom-sheet>` CE is currently a modal `<dialog>` opened with `showModal()` (see `openspec/specs/bottom-sheet-ce/spec.md` and `frontend/src/components/bottom-sheet/`). Dismiss is committed on `scrollsnapchange`/`pointerup`/`scrollend` heuristics that call `dialog.close()`, which then runs a fixed-duration (160ms) `opacity`+`overlay allow-discrete` fade. That fade is a second animation system, decoupled from and competing with the scroll-snap position, and `overlay allow-discrete` keeps the modal (and its pointer-blocking `::backdrop`) in the Top Layer for its whole duration.

Google/web.dev's `navigation-drawer` guide (retrieved via the `modern-web-guidance` skill) is the canonical pattern for a swipe-dismissible, scroll-snap-driven, Top-Layer overlay with a scroll-linked backdrop fade — the same UI this CE implements. It explicitly prefers scroll-snap over JS `transform` drag ("the scroll mechanism gives the user direct control ... and much more closely matches native mobile apps") and uses an `IntersectionObserver` as the single source of truth for state.

Constraints:
- Target browsers include iOS Safari (primary), Android Chrome, and desktop Chrome/Firefox/Safari (mobile-first PWA).
- CUBE CSS, Aurelia 2 CE conventions, Biome lint. See frontend AGENTS.md / `aurelia2-component` skill.
- The public CE contract (`open`, `dismissable` bindables; `sheet-closed` event) must not change — many consumers depend on it.

## Goals / Non-Goals

**Goals:**
- Eliminate bounce-back and the closing-window operation lock by construction, not by tuning.
- Adopt the web.dev `navigation-drawer` architecture adapted to a vertical bottom sheet.
- Preserve the scroll-linked backdrop fade and the existing public CE contract.
- Keep behavior correct on iOS Safari and Firefox (no reliance on Chromium-only features without a working cross-browser path).

**Non-Goals:**
- No JavaScript pointer-drag / `transform`-tween dismiss implementation (web.dev explicitly deprecates this vs scroll-snap).
- No change to consumer components' public API or to their history/`popstate` handling.
- No adoption of `scroll-initial-target` yet (see Decisions).
- No visual redesign of the sheet chrome (handle bar, radius, shadow, tokens unchanged).

## Decisions

### D1. `popover="manual"` instead of `<dialog>.showModal()`
A `popover` is non-modal: its `::backdrop` does not block background pointer events, and it does not force the background `inert`. This is precisely what unlocks the "tap another card during close" behavior. `popover="manual"` (not `auto`) is required so the browser's native light-dismiss does not fire mid-swipe. **Cost:** we lose the free focus-trap, `inert`, and ESC handling that `showModal()` provided; we re-implement them (D4). **Alternative considered:** keep `showModal()` and only defer `close()` until off-screen — rejected because a modal `::backdrop` blocks the background for the entire dismiss scroll regardless of when `close()` fires, so the operation lock cannot be fixed while remaining modal.

### D2. `IntersectionObserver` on the sheet body as the single source of truth
All dismiss paths (swipe, tap-outside, ESC, Android back, programmatic) reduce to "scroll the container to the closed stop"; the observer fires the actual `hidePopover()` + `sheet-closed` when the sheet body has left the viewport. This removes the `scrollsnapchange`/`scrollend`/`pointerup` heuristics and their magic ratios (`0.25`, `0.1`) entirely. **Alternative considered:** keep `scrollsnapchange` as primary with IO as fallback (the current spec's shape) — rejected because two detection systems is exactly the complexity that produced the drift and the iOS "flash then close" defect; IO alone covers all engines.

### D3. Close = scroll to the closed snap stop; hide only after off-screen
Dismiss never commits a `close()`/`hidePopover()` mid-gesture. It scrolls (`scroll-behavior: smooth`, honoring reduced-motion) toward the dismiss zone; the scroll itself, plus the scroll-timeline backdrop fade, is the animation. This is what makes the gesture interruptible (reverse = just scroll back = stays open, no bounce-back) and removes the need for the `pointer-events: none` lock. `hidePopover()` runs in the IO callback once the body is off-screen.

### D4. CE-managed focus-trap, `inert`, and Escape
- **`inert`**: apply to the app shell root (or `document.body` children outside the popover) on open; **remove it the moment a dismiss begins** (not at `hidePopover()`), so the closing window is interactive. For `dismissable="false"`, keep `inert` for the whole lifetime.
- **Focus**: record `document.activeElement` on open, move focus into the sheet body (`tabindex="-1"`), restore on close. A lightweight focus-trap (wrap Tab within the sheet) is added since `popover` does not trap.
- **Escape**: a `keydown` listener (Escape) initiates the dismiss scroll; suppressed when `dismissable="false"`.
- **Semantics**: set `role="dialog"` + `aria-modal="true"` + accessible name on the popover host (a `popover` has no implicit dialog role).

### D5. Keep the `initial-snap` keyframe hack; defer `scroll-initial-target`
The existing `initial-snap` keyframe (`--_snap-align: none`, `0.01s backwards`) snaps to the sheet body on open and works in all target engines. `scroll-initial-target: nearest` is the declarative web.dev alternative but is **Chromium-only** (Chrome/Edge 133+, unsupported in Safari desktop/iOS and Firefox as of 2026-08 per caniuse) and not Baseline. Adopting it would still require a rAF/`scrollTo` fallback that runs on our primary target (iOS Safari), making it strictly more complex than the keyframe hack. **Decision:** retain the keyframe hack now; add a code comment marking `scroll-initial-target: nearest` as the replacement to apply once it reaches Baseline.

### D6. `svh` and `overscroll-behavior: none`
`100dvh` → `100svh` on `.scroll-area`/`.dismiss-zone` and `90dvh` → `90svh` on `.sheet-body` so the sheet height does not jump when the iOS Safari address bar resizes mid-swipe. `overscroll-behavior-y: contain` → `overscroll-behavior: none` to fully stop the dismiss swipe from chaining into page scroll at the edges.

## Risks / Trade-offs

- **Re-implementing focus-trap/inert/ESC by hand can regress a11y** → Mirror web.dev's `navigation-drawer` guidance exactly (inert on shell, focus into sheet, Escape keydown); cover with unit tests for focus move/restore and an E2E keyboard-dismiss check; verify VoiceOver/TalkBack reach only sheet content when open.
- **`popover` API / scroll-driven animations browser support** → Popover is Baseline (since 2025-01, incl. iOS Safari 18.3+). The scroll-timeline backdrop fade is already `@supports`-gated with an opacity-transition fallback; keep that gate. Confirm iOS Safari popover version floor against the app's supported-OS matrix.
- **Non-modal means the background is technically live while open** → We still set `inert` on open, so behavior matches a modal until dismiss begins; only the *closing* window becomes interactive (the desired fix).
- **Spec/code drift already exists** (the current `bottom-sheet-ce` spec describes an IO-fallback + heuristic-removal state the shipped code does not fully match) → This change makes IO the single primary path and removes the heuristics, so the delta supersedes the drifted scenarios; the implementation and spec re-converge.
- **Reduced-motion**: a smooth dismiss scroll must collapse to instant under `prefers-reduced-motion: reduce` → gate `scroll-behavior: smooth` behind `@media (prefers-reduced-motion: no-preference)` (web.dev pattern) and jump-scroll otherwise.
- **Programmatic close during an in-flight open** → the just-opened guard (retained) plus IO settle detection prevent a self-close before the sheet settles on the body.

## Migration Plan

1. Frontend-only change; no proto/BSR/backend coordination. Ship via the normal frontend release once `make check` and E2E pass.
2. Implement in `frontend/src/components/bottom-sheet/` (`.ts`, `.html`, `.css`), update `bottom-sheet.spec.ts`.
3. Regression-guard: the artist-filter chip-check E2E (`contain: layout` stability) and add/extend swipe-dismiss + keyboard-dismiss + "tap card during close" coverage.
4. Smoke every consumer of `<bottom-sheet>` (event-detail-sheet, post-signup-dialog, date-range-sheet, artist-unfollow-sheet, user-home-selector, page-help) for open/close, dismissable vs non-dismissable, and focus behavior.
5. Rollback: revert the frontend PR; no data or schema migration involved.
6. At archive/sync time, update the `bottom-sheet-ce` main-spec `## Purpose` line (currently says `showModal()`) to reflect the `popover` architecture — the delta does not carry Purpose.

## Open Questions

- None that affect the specs, approach, or task breakdown. (The exact minimum iOS Safari version floor is a verification detail resolved during testing, not a design fork.)
