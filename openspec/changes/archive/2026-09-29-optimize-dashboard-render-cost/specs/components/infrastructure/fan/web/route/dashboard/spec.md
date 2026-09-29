## MODIFIED Requirements

### Requirement: Highlighted card visuals must not drive continuous rendering work

A concert card's visual treatment MUST NOT force the browser to recompute style or
layout on every animation frame while the timetable is idle. This applies in
particular to highlighted (hype-matched) cards, whose emphasis effect must not run
a perpetual per-frame style/paint invalidation.

#### Scenario: Idle timetable does no continuous rendering work

- **WHEN** the dashboard timetable is displayed and the fan is not interacting with
  it
- **THEN** over a 3-second idle capture on the reference profile, the Recalculate
  Style and Layout self-time attributable to card visuals is negligible (no ongoing
  per-frame recalculation)

#### Scenario: Reduced motion is respected

- **WHEN** the fan's system requests reduced motion (`prefers-reduced-motion:
  reduce`)
- **THEN** the timetable presents cards without animated motion
