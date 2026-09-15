## Context

See proposal.md — Why. Constraints that shape this design:

- The bottleneck is proven by a real-device DevTools trace: **Layout 46% +
  Recalculate Style 32%** of a 7.4 s INP; Paint 2.8%; scripting small; backend
  and RPC fast. So the fix must target Style-recalc and Layout, and its success
  must be judged by re-measuring those, not by intuition. (An earlier "paint" and
  "RPC latency" hypothesis were both disproven by measurement.)
- The two levers with the highest ratio of impact to change size are CSS-only:
  stop the continuous custom-property animation (Style) and add viewport
  containment (Layout). They are independent and additive.
- The Aurelia rendering model is direct DOM binding with keyed `repeat.for`
  (`key.bind: ev.id` / `group.dateKey`) already in place, so DOM is reused across
  re-entry — the residual cost is style/layout recalculation, exactly what P1+P2
  target. (Aurelia 2.x; keyed-repeat / `virtual-repeat` / `batch()` confirmed
  against Context7 `/aurelia/aurelia`, 2026-09-12.)

## Goals / Non-Goals

**Goals:**

- Cut the entry/re-entry main-thread rendering cost (Layout + Recalculate Style)
  by removing the continuous style-invalidation source and by not laying out
  off-screen cards.
- Keep the change CSS-only and reversible, gated on before/after measurement.

**Non-Goals:**

- No change to RPC/store/route logic, the `dateGroups` refetch, or the laser-beam
  JS geometry loop (that is P3/P4, deferred).
- No list virtualization / structural flattening in this change (P4).
- No visual redesign — cards keep their identity; only continuous motion is
  removed or reduced-motion-gated.

## Decisions

- **Decision (UPDATED): Ship P1 only; P2 was implemented, measured, then
  reverted.** P1 and P2 were originally shipped together (measure-after-each), and
  the prod measurement confirmed P2's Layout win (forced reflow 751 ms → 528 ms,
  −30%). But P2 then caused two prod regressions and was reverted (see the
  superseding decision below). The change as shipped is **P1 only**. The earlier
  per-lever measurement rationale still stands historically, but the P2 decisions
  further down are SUPERSEDED.

- **Decision (SUPERSEDING): Revert P2 (`content-visibility`) — it is incompatible
  with this component.** `content-visibility: auto` ALWAYS establishes layout,
  paint, and style (and, when off-screen, size) containment, which conflicts two
  ways here:
  1. On the date-group `<li>` (`grid-template-columns: subgrid`), the containment
     **disables the subgrid** — computed `grid-template-columns` collapses to
     `none`, so the three lane columns lose their tracks and every card spans the
     full row (measured on prod: lane 363 px / card 345 px vs the correct
     121 px / 103 px).
  2. Moving it to `.lane` (a plain grid item) keeps the subgrid intact, but paint
     containment then **clips the matched card's spotlight `box-shadow`** (up to
     `0 0 80px`) at each lane's ~8 px-padded box.
  The only cross-content un-clip mechanism, `overflow-clip-margin`, requires
  `overflow: clip`, which disables the sticky date-separator (its layout context) —
  and it is not supported in Safari — so there is no viable placement. A correct
  viewport-scoping needs the **P4 group→lane→card flatten** so containment can
  live on a non-subgrid, full-row element that does not clip the glow. P2 is
  therefore deferred to P4 (a separate change).

- **Decision: Delete the `--hue-drift` animation outright — it drives a dead
  variable.** `--hue-drift` only feeds `--artist-color` / `--artist-color-dim` (via
  the `[artist-color]` rule), and `var(--artist-color)` has ZERO consumers in the
  codebase — the matched card's border/gradient/box-shadow are built from the raw
  `--artist-hue`. So the animation forces a full-subtree style recalc per frame for
  no visible output. The fix is therefore a **pure deletion** (animation,
  `@property --hue-drift`, and the dead `--artist-color`/`--artist-color-dim`
  derivations), NOT a "static replacement" — there is no animated visual identity
  to preserve. A before/after screenshot confirms no visual change. (Even if some
  motion were later wanted, it MUST use a compositor-only property like
  `transform`/`opacity`, never a custom property.)

- **Decision (SUPERSEDED — see the revert decision above): Apply
  `content-visibility: auto` + `contain-intrinsic-size: auto <fallback>` to the
  date-group `<li>`, not per event-card or per virtualization.**
  Rationale: the date-group `<li>` is the natural scroll chunk (a whole day's lanes
  enter/leave the viewport together); per-card is too granular (containment
  bookkeeping overhead on many small cells that also sit in a subgrid). Use the
  `auto` keyword on `contain-intrinsic-size` so the browser caches each group's
  real rendered height and reuses it on re-reveal — the literal fallback only
  covers the first paint before a group has ever rendered, so a slightly-off
  fallback cannot cause a persistent scrollbar jump. `content-visibility` is a
  per-element CSS attribute needing no structural change, whereas `virtual-repeat`
  requires flattening the nested group → lane → card structure; ship containment
  first and escalate to `virtual-repeat` (P4) only if measurement shows containment
  is insufficient for large timetables. (When P4 is actually scoped, confirm
  `@aurelia/ui-virtualization` is installable at the repo's pinned `@aurelia`
  version — the API is documented for Aurelia 2, but package availability per
  release must be verified then, not assumed now.)

- **Decision (SUPERSEDED — this reasoning was WRONG): Applying size containment to
  the subgrid group `<li>` is safe because the parent columns are
  content-independent.** This assumed only *size* containment mattered and only
  when off-screen. In reality `content-visibility: auto` also applies *layout* and
  *paint* containment while on-screen, and that **disables subgrid entirely**
  (computed `grid-template-columns: none`), collapsing the columns regardless of
  the parent's fixed `1fr 1fr 1fr`. This is the root cause of the shipped
  lane-overflow bug; it is why P2 was reverted. (The `1fr 1fr 1fr` columns are
  fixed, so with NO containment the subgrid is not needed for alignment per se, but
  the `hideAway` collapse relies on subgrid propagation — so the subgrid must
  stay, and containment must not sit on it.)

## Risks / Trade-offs

- **`content-visibility: auto` needs a sane `contain-intrinsic-size`** →
  a wrong estimate causes scrollbar jump / layout shift (CLS is currently 0 —
  must stay 0). Mitigation: use `contain-intrinsic-size: auto <fallback>` so the
  browser caches each group's real rendered height after first paint; pick the
  literal fallback from a typical group height (it only affects the never-rendered
  first paint). Verify CLS in the after-trace.
- **Removing the hue drift is a visible change** → Mitigation: it is intentional
  and called out in the proposal; confirm the static/gradient treatment still
  reads as on-brand with the design owners.
- **Measurement variance on the reference profile** → Mitigation: measure the
  same interaction (nav-tab tap) on the same emulated profile (Pixel 8 / 4× CPU)
  before and after, and cross-check with PostHog `web.vitals` on `/dashboard`.
- **P1+P2 alone may not reach the absolute "good" CWV thresholds** → This is why
  the spec's acceptance scenarios are framed as a SUBSTANTIAL reduction versus the
  recorded baseline (Style + Layout no longer dominating), with the absolute good
  thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms) as the capability's cumulative end state,
  not this change's pass/fail gate. So there is no contradiction between the spec
  and this partial change; a large-but-not-"good" result still satisfies the spec
  and simply feeds the P3/P4 decision.
- **`content-visibility: auto` (P2) interacts with the live laser-beam JS** — the
  beam positioner reads `getBoundingClientRect()` / `querySelectorAll(
  '[data-beam-index]')` on cards that would now sit under containment; off-screen
  subtrees are render-skipped. → Mitigation: task 3.3 verifies beams do not vanish
  / mis-position after containment; if they regress, the fix is routed to P3 (the
  beam JS is out of scope here), not bolted onto this change.

## Migration Plan

- CSS-only; ships with the normal frontend release. Rollback = revert the CSS
  edits (no data or API surface touched).

## Open Questions

- **RESOLVED — `position: sticky` × containment** is moot now that P2 is reverted:
  with no `content-visibility` on the `<li>`, the date-separator sticky behavior is
  unchanged from before this change. (This interaction resurfaces only if P2 is
  re-attempted under P4.)

## Follow-ups (separate changes — NOT this change)

- **P4 — viewport-scoping done right.** Flatten group → lane → card so
  `content-visibility` can live on a non-subgrid, full-row element that neither
  disables subgrid nor clips the matched card's glow; then re-measure the Layout
  win P2 demonstrated (751 ms → 528 ms forced reflow). Also confirm
  `@aurelia/ui-virtualization` is installable at the repo's pinned `@aurelia`
  version if virtualization is chosen.
- **P3 — beam `getBoundingClientRect()` scroll cost** (the beam JS is already
  scroll-driven and read/write-phase-separated, so this is gBCR cost, not a
  forced-reflow loop).
- **Header/nav paint starvation on re-entry (discovered during verification).**
  instant-page-switch updates the header/nav STATE at navigation-start, but the
  dashboard's cache fast-path sets `dateGroups` synchronously in `loading()`, so
  Aurelia flushes the header-binding update and the heavy 23-group timetable render
  in the same task → a single paint after the render (INP 2536 ms on the
  authenticated real-device capture, Measurement B). The header/nav therefore
  appear to wait for the render even though the
  state is decoupled. Fix candidate: yield a frame before the heavy render (defer
  the cache-paint out of the synchronous `loading()` path) and/or the P4 flatten +
  virtualization. Belongs with P3/P4, not this change.
