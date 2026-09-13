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

- **Decision: Ship P1 and P2 as one CSS change, but measure after each.**
  Rationale: both are small and CSS-only, but they attack different trace
  segments (Style vs Layout), so measuring after P1 alone tells us how much of
  the 32% Style cost it removed before P2 muddies attribution. Alternative
  (one big change P1–P4) rejected: the earlier mis-attribution shows we must
  re-measure before assuming the next lever is needed.

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

- **Decision: Apply `content-visibility: auto` + `contain-intrinsic-size: auto
  <fallback>` to the date-group `<li>`, not per event-card or per virtualization.**
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

- **Decision: Applying size containment to the subgrid group `<li>` is safe
  because the parent columns are content-independent.** The `<li>` participates in
  `grid-template-columns: subgrid`, and size containment normally risks breaking a
  subgrid item's track contribution — but the parent grid defines fixed
  `1fr 1fr 1fr` columns at `:scope`, so the column line positions do not depend on
  any group's content. Skipping an off-screen group's rendering therefore cannot
  shift the columns. (Verified by task 3.2 — confirm no column drift.)

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

- **`position: sticky` × containment.** `content-visibility: auto` implies
  `contain: layout paint`, which makes the date-group `<li>` a containing block and
  confines the `.date-separator` (`position: sticky; inset-block-start: 0`) to its
  own group's box. This changes sticky behavior: the date header would hand off at
  each group boundary (section-style sticky) rather than persisting across the
  whole scroll. Whether that matches the intended UX must be confirmed against the
  current behavior and on the reference profile (task 3.3 / the new spec scenario).
  If it is a regression, the mitigation is to lift `content-visibility` off the
  `<li>` and onto an inner wrapper below the sticky header — but that wrapper must
  not itself be a subgrid participant, so it needs checking before adopting.
- The scope of any follow-up (P3 beam `getBoundingClientRect()` cost, P4
  virtualization) is deliberately decided AFTER the P1+P2 re-measurement.
