<!-- change: optimize-dashboard-render-cost | old_cap: dashboard-timetable-rendering -->
### Requirement: Timetable rendering cost is bounded and must not dominate the main thread

Displaying the dashboard timetable — on first navigation and on tab-switch
re-entry — MUST NOT be dominated by browser Layout and Style-recalculation work,
and MUST NOT style or lay out off-screen content. Rendering cost is dominated by
Layout and Recalculate Style, not by network or backend latency, so this contract
constrains main-thread rendering only; the backend/RPC path is out of scope.

Measurements are taken on the reference profile — a mid-tier mobile device (e.g.
Pixel 8) or a desktop emulating it with 4× CPU throttling — against a recorded
pre-change baseline, so the contract reflects real fan devices.

The "good" Core Web Vitals thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms) are the
capability's target END STATE, reached cumulatively across this and any follow-up
rendering work. A single change satisfies this requirement by delivering a
substantial, measured reduction toward that end state — not necessarily the
absolute thresholds in one step.

#### Scenario: Tab-switch re-entry does not freeze on rendering

- **WHEN** an authenticated fan with a populated timetable taps the dashboard
  navigation tab from another tab
- **THEN** the tap's Interaction to Next Paint (INP), measured on the reference
  profile, is substantially lower than the recorded pre-change baseline, and the
  Layout + Recalculate Style self-time for the interaction no longer dominates the
  main-thread cost
- **AND** the timetable content appears without a multi-second blank/skeleton gap

#### Scenario: First dashboard load render cost is reduced

- **WHEN** an authenticated fan with a populated timetable loads the dashboard
- **THEN** Largest Contentful Paint (LCP) on the reference profile is substantially
  lower than the recorded baseline, with its render-delay (main-thread) portion no
  longer dominated by Layout + Recalculate Style

#### Scenario: Off-screen timetable content is not styled or laid out eagerly

- **WHEN** the timetable contains more concert cards than fit in the viewport
- **THEN** style and layout work for cards outside the viewport does not contribute
  to the entry/re-entry main-thread cost

#### Scenario: Viewport-scoping off-screen content does not regress sticky headers or shift layout

- **WHEN** a fan scrolls across multiple date groups whose off-screen content is
  viewport-scoped (skipped when off-screen)
- **THEN** the date separator's sticky behavior is intentional and consistent
  across groups (either it persists at the top or it hands off at each group
  boundary — not a mix), and no cumulative layout shift is introduced (CLS stays 0)
  as groups scroll in and out

<!-- change: optimize-dashboard-render-cost | old_cap: dashboard-timetable-rendering -->
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

