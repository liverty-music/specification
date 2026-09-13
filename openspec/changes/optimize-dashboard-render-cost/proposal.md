## Why

The fan-web dashboard (My Timetable) is slow to display on both first load and
tab-switch re-entry. A DevTools performance trace on the real device (Pixel 8)
measured **INP 7,419 ms** (nav-tab tap) and **LCP 4.94 s**, with the main-thread
time dominated by **Layout 46% + Recalculate Style 32%** (Paint only 2.8%,
scripting small). Backend and network are NOT the cause: fan-api RPC access logs
show p50 7–93 ms / max 480 ms, and the client RPC calls settle in 50–216 ms. The
earlier "RPC latency" signal in PostHog was the main-thread block delaying the
RPC promise callback, not real network/backend latency. The bottleneck is
purely client-side rendering.

Two root causes account for the measured 78% (Layout + Recalculate Style):

1. **Recalculate Style (32%)** — every hype-matched (highlighted) concert card
   (`.event-card[data-matched]`) runs an infinite CSS animation (`color-drift 8s
   infinite`) that animates a **registered CSS custom property** (`--hue-drift`,
   declared via `@property`). Animating a custom property is not
   compositor-friendly and forces a full-subtree style recalculation every frame,
   for every matched card, forever. (Unmatched cards do not carry this animation.)
   Worse, this cost buys nothing visible: `--hue-drift` only feeds `--artist-color`
   / `--artist-color-dim` (via the `[artist-color]` rule's `calc()`), and
   `var(--artist-color)` has **zero consumers** anywhere in the codebase — the
   matched card's border, gradient, and box-shadow are all built from the raw
   `--artist-hue`. So `color-drift` pays a full-subtree style recalc every frame
   while producing **no visible output**; it is pure waste.
2. **Layout (46%)** — the timetable renders a large DOM with **no CSS
   containment** (`content-visibility` / `contain` are absent), so any style or
   layout invalidation recomputes layout over the entire tree. The DevTools
   "Optimize DOM size" and "Forced reflow" insights both flag this.

## What Changes

- **P1 — Stop the per-frame style-recalc driver (pure deletion).** Delete the
  `color-drift` animation, the `@property --hue-drift` declaration, and the
  now-dead `--artist-color` / `--artist-color-dim` derivations in the
  `[artist-color]` rule (they have zero consumers). Separately, delete the
  `contact-glow` / `pulse-glow` keyframes, which are also DEAD (defined but applied
  to no element). No static replacement is needed: because the animated custom
  property fed no visible output, the matched card keeps its full neon identity
  from its existing static gradient / border / box-shadow. A before/after
  screenshot of a matched card confirms the deletion is visually a no-op.
- **P2 — Scope layout and style to the viewport.** Apply
  `content-visibility: auto` + `contain-intrinsic-size: auto <fallback>` to the
  **date-group `<li>`** (the natural scroll chunk), not per event-card, so
  off-screen groups skip style and layout work. The `auto` keyword lets the
  browser cache each group's real rendered height, eliminating re-reveal layout
  shift; the literal fallback only applies before a group has ever rendered.
- **Measurement gate.** Re-run the DevTools performance trace and PostHog
  `web.vitals` (route `/dashboard`) after P1, then after P2, to confirm the
  Layout + Recalculate Style reduction before deciding whether the deferred
  P3/P4 work is still needed.

Out of scope (deferred to a follow-up change once P1+P2 are measured):

- **P3** — the laser-beam JS is ALREADY scroll-driven (not per-frame), ALREADY
  read/write-phase-separated (reads all `getBoundingClientRect()` before any style
  write, so no forced reflow), and caches its element lookups. The residual P3
  concern is the `getBoundingClientRect()` cost during large scrolls, NOT a
  forced-reflow loop — a follow-up must be scoped against the real measured
  residual, not the original (now-inaccurate) "per-frame forced reflow" framing.
- **P4** — `virtual-repeat` (`@aurelia/ui-virtualization`) list virtualization and
  batching/skip-on-unchanged for the `dateGroups` reassignment. This needs the
  nested group → lane → card structure flattened and is a larger refactor.

## Capabilities

### New Capabilities

- `dashboard-timetable-rendering`: The performance and motion contract for
  rendering the fan-web dashboard timetable — an entry/re-entry rendering budget
  (no multi-second main-thread block) and the rule that card visuals must not
  drive continuous per-frame style/layout invalidation, respecting
  `prefers-reduced-motion`.

### Modified Capabilities

<!-- None — no existing spec captures dashboard timetable rendering. -->

## Impact

- **Frontend only** (no proto / backend / API change):
  - `frontend/src/components/live-highway/event-card.css` (P1: animations;
    P2: containment)
  - `frontend/src/components/live-highway/concert-highway.css` (P2: containment;
    beam animations audit)
- **Behavior change**: none visible. The removed `color-drift` animated a custom
  property with no consumer, so deleting it leaves the matched card's appearance
  unchanged (confirmed by before/after screenshot). The change is purely a
  render-cost reduction.
- **Interaction to verify (P2 × existing beam JS)**: `content-visibility: auto`
  skips rendering of off-screen subtrees. The laser-beam positioning
  (`concert-highway.ts` — `getBoundingClientRect()` / `querySelectorAll(
  '[data-beam-index]')`) reads card geometry and is NOT changed here (that is P3).
  P2 must confirm the beams do not visually regress (vanish / mis-position) once
  containment is applied.
- **No RPC/store/route logic change** in this change (the `dateGroups` refetch and
  beam JS reflow are P3/P4, deferred).
- **Verification**: DevTools performance trace (INP/LCP + Bottom-up Layout/Style
  self-time) and PostHog `web.vitals` / `perf.long_animation_frame` on
  `/dashboard`, before/after.
- CSS specifics (exact `content-visibility` / `contain-intrinsic-size` values,
  animation replacement) are owned by the cube-css / web-design-specialist
  conventions.
