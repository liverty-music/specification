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

- **Decision: Remove the continuous `--hue-drift` animation rather than optimize
  it.** Animating a CSS custom property cannot be composited and forces
  full-subtree style recalc per frame; there is no "cheap" version. Replace with a
  static treatment. Alternative (animate a compositor-only property like
  `transform`/`opacity`, or a fixed gradient) is acceptable if the visual must
  keep some motion — but it MUST NOT re-introduce per-frame Style/Layout. The
  exact CSS is owned by cube-css / web-design-specialist.

- **Decision: Use `content-visibility: auto` + `contain-intrinsic-size` for
  viewport-scoped layout, not virtualization.** Rationale: it is a per-element CSS
  attribute needing no structural change, whereas `virtual-repeat` requires
  flattening the nested group → lane → card structure. Ship containment first;
  escalate to `virtual-repeat` (P4) only if measurement shows containment is
  insufficient for large timetables. (When P4 is actually scoped, confirm
  `@aurelia/ui-virtualization` is installable at the repo's pinned `@aurelia`
  version — the API is documented for Aurelia 2, but package availability per
  release must be verified then, not assumed now.)

- **Decision: Gate any retained motion on `prefers-reduced-motion`.** Matches the
  spec's motion requirement and the existing reduced-motion handling in the card
  CSS.

## Risks / Trade-offs

- **`content-visibility: auto` needs a good `contain-intrinsic-size`** →
  a wrong estimate causes scrollbar jump / layout shift (CLS is currently 0 —
  must stay 0). Mitigation: set intrinsic size from the real card height; verify
  CLS in the after-trace.
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

- None that block P1+P2. The scope of any follow-up (P3 beam reflow, P4
  virtualization) is deliberately decided AFTER the P1+P2 re-measurement.
