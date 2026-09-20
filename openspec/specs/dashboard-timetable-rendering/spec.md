# dashboard-timetable-rendering Specification

## Purpose

Defines the rendering performance and motion contract for the fan-web dashboard
timetable (My Timetable), so that showing the followed-artist concert list on
entry and on tab-switch re-entry stays responsive and does not block the main
thread, independent of how the list is implemented.

## Requirements

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

### Requirement: The timetable frame paints without data

The dashboard timetable's data-independent structure — the stage header naming
the lanes, and the lane columns themselves — SHALL be painted as soon as the
route's view attaches, before any concert data is available. While data is
pending the view SHALL present a placeholder shaped like the timetable, and it
SHALL NOT present an empty state. An empty state SHALL be shown only once a load
has settled and genuinely returned no concerts; it SHALL NOT be derived from the
rendered group count alone, which cannot distinguish "not yet assigned" from
"genuinely zero".

#### Scenario: Frame appears before any concert data

- **WHEN** a fan navigates to the dashboard and the concert data has not arrived
- **THEN** the stage header and lane columns SHALL be visible
- **AND** a timetable-shaped loading placeholder SHALL occupy the lanes
- **AND** neither the "no concerts" empty state nor the guest empty state SHALL
  be rendered

#### Scenario: Empty state waits for a settled load

- **WHEN** a load settles and returns zero concerts
- **THEN** the empty state SHALL be rendered
- **AND** it SHALL NOT have appeared at any earlier point during that load

### Requirement: Timetable rendering is scoped to the viewport

Rendering work for the timetable SHALL be bounded by what the fan can see: date
groups outside the viewport SHALL skip style, layout and paint work, and SHALL be
rendered as they are scrolled into view. Lane alignment with the stage header
SHALL be preserved for every group, in both the three-lane and the collapsed
two-lane (All Nearby) presentations. The scroll extent SHALL remain stable enough
that scrolling does not jump and that a restored scroll position lands within one
card of where the fan left.

#### Scenario: Off-screen dates are not rendered

- **WHEN** a populated timetable is displayed
- **THEN** date groups outside the viewport SHALL NOT incur style, layout or
  paint work
- **AND** scrolling toward them SHALL render them in time to be seen

#### Scenario: Lanes stay aligned under viewport scoping

- **WHEN** any date group is rendered, on screen or newly scrolled into view
- **THEN** its lane columns SHALL align with the stage header's columns
- **AND** this SHALL hold in both the three-lane and the two-lane presentations

### Requirement: Re-entry restores the date the fan was looking at

On re-entry to a timetable the fan has already seen, the cached content SHALL be
restored showing the same date group the fan left it on, at any scroll depth.

The position SHALL be remembered as the date it identifies, not as a pixel
offset. Under viewport-scoped rendering an off-screen group's height is an
estimate until it renders, and the browser's memory of each real height does not
outlive the elements — which navigation destroys — so a pixel offset taken
before the trip denotes a different place after it, increasingly so with depth.

Restoring SHALL happen once the content is rendered: before that the anchored
group does not exist and the restore is silently lost. A date that is no longer
in the list SHALL leave the fan where they are rather than resolve to a
substitute.

#### Scenario: Re-entry restores the same date, at any depth

- **WHEN** a fan scrolls deep into the timetable, navigates to another tab, and
  returns
- **THEN** the timetable SHALL show the same date group it showed when they left
- **AND** this SHALL hold as far down the timetable as the content goes, not only
  near the top

#### Scenario: The anchored date is gone

- **WHEN** the timetable is restored but a background refresh has dropped the
  date the fan left it on
- **THEN** the view SHALL stay where it is rather than scroll to a substitute
  date

### Requirement: Page identity paints independent of the timetable render

On dashboard tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — SHALL NOT be held hostage to the timetable's render.
The re-entry render SHALL be bounded by what is visible, so that page identity
and timetable arrive together within an interaction budget rather than the shell
waiting on an unbounded render. Reflecting timetable render state SHALL NOT be
performed in a pre-activation route lifecycle hook. Re-entry SHALL NOT lose the
background refresh, the data-ready celebration/onboarding latch, or an in-flight
deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the dashboard navigation tab from another tab
- **THEN** the tap's Interaction to Next Paint SHALL be substantially lower than
  the pre-change baseline
- **AND** the render work for that interaction SHALL be bounded by the visible
  portion of the timetable, not by the full set of loaded date groups

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is reflected from the component lifecycle
- **THEN** the background refresh SHALL still fetch and swap in fresh data
- **AND** the data-ready celebration / onboarding-completion latch SHALL still
  fire once when due, and a pending `/concerts/:id` deep-link SHALL still open
  the detail sheet
