## Why

The `<concert-highway>` laser-beam scroll tracking is the heaviest runtime JavaScript on the dashboard and Welcome-preview hot path (surfaced during a NoLoJS review). Its per-frame update does a per-beam `querySelector` DOM lookup and interleaves layout reads (`getBoundingClientRect`) with style writes (`setProperty`) inside one loop — a classic layout-thrash shape that costs INP on mobile for no visual benefit. A full move to CSS scroll-driven animations was evaluated and rejected (non-linear beam geometry, dynamic per-card timelines, and a mandatory iOS/Safari `@supports` fallback since no browser-support policy is declared), so this change instead removes the JS inefficiencies directly, with zero behavior change.

## What Changes

- Refine the beam-tracking rendering contract so each `requestAnimationFrame` update: (a) resolves each beam's anchor card via a **cached anchor→element map** rebuilt only when inputs change, instead of a per-frame `querySelector`; and (b) performs **all layout reads before any style writes** (no read/write interleave). Visual output is identical.
- Remove the dead `@keyframes beam-descend` from `event-card.css` (added by the festival-spotlight change, never referenced by any `animation:` — confirmed via repo-wide grep). Housekeeping only.

Non-goals (explicitly deferred): replacing the JS beam tracking with CSS scroll-driven animations (`animation-timeline: view()`), altering beam appearance/geometry, or changing the `clip-path` cone.

## Capabilities

### New Capabilities

<!-- none — no new capability is introduced. -->

### Modified Capabilities

- `concert-highway-ce`: refine the "Laser beam effects for matched events" scenario to add a rendering-efficiency invariant (cached anchor→element resolution and batched read-before-write per rAF). The observable beam behavior is unchanged; the requirement pins the non-functional guarantee so the optimization cannot silently regress.

## Impact

- `frontend`: `src/components/live-highway/concert-highway.ts` (`updateBeamPositions`, beam-map lifecycle), `src/components/live-highway/event-card.css` (dead keyframe removal).
- No API, proto, or backend impact. No dependency changes.
- Performance: fewer DOM queries and no interleaved forced reflow per scroll frame on the dashboard + Welcome preview (INP hygiene).
- Ship target: merged and released to prod (frontend release), consistent with the healthy v1.24.0 baseline.
