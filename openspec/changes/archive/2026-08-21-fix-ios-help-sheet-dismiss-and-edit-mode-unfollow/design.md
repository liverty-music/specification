# Design

## Context

See proposal.md — Why. Two iOS-only touch defects, both from WebKit/Blink engine differences:

- **Help sheet**: `<bottom-sheet>` (shared by page-help, event-detail, post-signup, user-home-selector, …) uses CSS scroll-snap for swipe-to-dismiss. A WebKit Playwright repro captured the mechanism precisely: on open, the CSS `initial-snap` trick lands the scroll on `.sheet-body` (ratio `1`), then WebKit re-snaps to the dismiss zone (ratio `0`) as the animation ends. The fallback heuristics `onScrollEnd` (`scrollRatio < 0.1`) and `onPointerUp` (`scrollTop/max < 0.25`) — added under the now-stale assumption "Safari lacks `scrollsnapchange`" — fire on that *programmatic* re-snap and call `requestClose()`. Measured ratio trace: `[1, 0]`; `dialog.open` timeline: `true×7 → false×8`. Chromium never reproduces (it keeps `scrollsnapchange` + a stable initial snap).
- **Long-press unfollow**: the list row's hidden 500 ms long-press is cancelled by the iOS system gesture (`pointercancel`), and the visible trash column is hidden on `pointer: coarse`, so touch users have no working unfollow.

Constraints: Aurelia 2 SPA, CUBE CSS, Biome, no inline styles (lint), frontend-only (no proto/RPC), ship via frontend release.

## Goals / Non-Goals

**Goals**
- Sheet reliably stays open on iOS until a genuine user dismiss.
- Unfollow works on every pointer type via a discoverable, accessible, single-pointer affordance.
- Net reduction in bespoke gesture/heuristic code; align with web-standard primitives.
- A regression guard that actually runs on the WebKit engine.

**Non-Goals**
- No re-introduction of any swipe or long-press unfollow.
- No change to the follow-store unfollow flow, Undo mechanism, or backend.
- No rework of the bottom-sheet's open/`initial-snap`/inert/focus-trap architecture (kept as-is).
- Grid (Festival) view and its long-press context menu are out of scope (already removed from the frontend; residual spec drift is a separate cleanup).

## Decisions

### D1: Edit-mode toggle over swipe or long-press for list unfollow
Chosen: an iOS-style "Edit" toggle in the header reveals a per-row remove (−) control; single tap → immediate unfollow + Undo.

Rationale & alternatives:
- **Long-press (current)** — hidden, non-discoverable, conflicts with the iOS system gesture; broken on iOS. Rejected.
- **Swipe-to-reveal** — attempted twice historically and abandoned both times: v1 JS-transform swipe (main-thread jank, extra DOM layers, #174 proposal), then v2 CSS scroll-snap horizontal swipe (nested vertical-list × horizontal-row scroll and, critically, the in-row interactive hype radios conflicting with the horizontal gesture — reverted within ~1 week). The row still contains interactive hype radios, so any in-row gesture re-hits that wall. Rejected as high-risk "attempt #3".
- **Always-visible per-row button** — clutters a dense list (name + 4 hype columns). Rejected on UX grounds.
- **Edit mode** — no gesture, no scroll/tap conflict, single-pointer (WCAG 2.5.1 Level A), the iOS HIG standard pairing, and default list stays uncluttered. Chosen.

Placement & scope:
- The Edit toggle lives in the shared `page-header` `<au-slot>`, on the trailing side of the title, next to the existing `<page-help>` (`?`) control (iOS "Edit top-trailing" convention). It renders only in the populated state — hidden while loading and in the empty (zero-artist) state.
- **Unified across pointer types** (decision): the desktop-only always-visible trash column is removed too; both `pointer: fine` and `pointer: coarse` use Edit mode. Rationale: a single affordance and code path, consistent with the spec's "no persistent per-row control." Trade-off: desktop unfollow becomes two clicks (Edit → −) instead of one; accepted for consistency and reduced surface.
- Lifecycle: edit mode auto-exits when the list empties and is not persisted across navigation (fresh, non-editing on re-entry). Hype controls remain interactive while editing.

### D2: `scrollsnapchange` as the primary dismiss signal; delete scroll-ratio heuristics
Chosen: detect user swipe-dismiss via `scrollsnapchange` (fires only on user scroll gestures per the CSS Scroll Snap module), and DELETE `onScrollEnd`/`onPointerUp` scroll-ratio heuristics.

Rationale & alternatives:
- **Add a user-engagement flag to the existing heuristics ("Fix②-only, bolted on")** — works, but *adds* state to fragile code and keeps the misfiring signals. Inferior.
- **Use `scrollsnapchange`** — the platform already guarantees the user-vs-programmatic distinction we need, so the programmatic `[1→0]` re-snap cannot fire it. This is a net code *deletion*, matches the canonical reference implementation (viliket/pure-web-bottom-sheet) and Chrome for Developers guidance, and satisfies the "don't over-complicate" constraint. Chosen.
- Support: `scrollsnapchange` is in Chrome 129+ and Safari 18.2+ (the app targets latest browsers; iOS 26 qualifies). The stale "Safari lacks `scrollsnapchange`" comment is corrected.

### D3: `IntersectionObserver` fallback + just-opened guard (not `scrollend`-ratio)
For engines without `scrollsnapchange` (Firefox), detect dismiss via an `IntersectionObserver` on the dismiss zone / sheet-body, armed only after the sheet settles on `.sheet-body`. Keep a small "just-opened" guard suppressing any dismiss until settled. The reference implementation does the same (`checkVisibility()` / transition-state guard). This mirrors D2's robustness on non-supporting engines without resurrecting scroll-ratio guessing.

### D4: Keep the CSS `initial-snap` trick
It is the canonical way to land a scroll-snap sheet on its body without JS `scrollTo`, and the reference implementation uses it too. The bug was never the initial snap itself but the heuristics misreading the subsequent programmatic re-snap. Left unchanged.

### D5: WebKit regression test as the acceptance gate
A real-WebKit Playwright project (`webkit-repro`, iPhone 14) plus a `chromium-control` on the same viewport. The spec asserts the help sheet opens and stays open. RED before the fix, GREEN after. Rationale: Chromium device emulation cannot reproduce engine-difference bugs; only a real WebKit engine can. These projects are opt-in (not in the default CI selection / require the WebKit browser) so they don't destabilize existing Chromium-only CI.

## Risks / Trade-offs

- **[Risk] With heuristics removed, WebKit could rest the scroll on the dismiss zone (ratio 0) → sheet "open but blank".** → The `initial-snap` trick lands on `.sheet-body` first; the just-opened guard + settle detection re-assert the body position. The `webkit-repro` test asserts the sheet content is actually visible (not merely `open`), so this failure mode is caught before merge; if observed, add a one-line deterministic `scrollTop = maxScroll` on settle (still no heuristic guessing).
- **[Risk] `scrollsnapchange` unsupported on older/other engines.** → `IntersectionObserver` fallback (D3); no reliance on `scrollend`-ratio.
- **[Risk] Edit-mode discoverability lower than an always-visible control.** → The visible "Edit" label is self-describing; help copy updated to document it; matches a pattern iOS users already know.
- **[Risk] Removing `ArtistUnfollowSheet` / `long-press` could touch shared wiring (main.ts registration, i18n keys, page-help section).** → Enumerated in Impact; unit tests updated; `make check` gate.
- **[Risk] Bundling two concerns (sheet fix + unfollow redesign) in one change.** → They share the same iOS-touch root theme and the same files region; kept in one change for a single release, with independent tasks so either can be reverted in isolation.

## Migration Plan

1. Land frontend changes behind normal review; `make check` + unit/E2E green; `webkit-repro` GREEN, `chromium-control` GREEN.
2. Merge to `main`; cut a frontend release (GH Release → prod AR retag → automated pin-bump → ArgoCD sync), per project convention.
3. Verify on a real iOS device: help sheet opens and stays open; Edit mode unfollow + Undo works.
4. Rollback: revert the PR / roll back the release pin. No data migration (frontend-only; unfollow flow unchanged).

## Open Questions

- Whether the settle guard alone keeps the sheet content visible on WebKit, or a one-line deterministic `scrollTop` re-assert is also needed (D5 / first Risk). Safely deferrable: it does not change the specs, the chosen approach, or the task breakdown — the `webkit-repro` test resolves it during implementation.
