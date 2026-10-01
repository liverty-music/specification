## ADDED Requirements

### Requirement: The timetable renders a window of dates around the fan

The timetable SHALL build only the date groups in a window around where the fan
is looking, not every loaded date. On a first visit the window starts at the
first date; on re-entry it starts at the date the fan left the timetable on.
As the fan scrolls toward either edge of the window, further dates SHALL be
added on that side before the fan reaches the edge, so scrolling never stops at
an artificial end. Adding dates above the fan SHALL NOT move what the fan is
looking at. Dates outside the window SHALL NOT be built. Lane alignment with the
stage header SHALL hold for every group, in both the three-lane and the
collapsed two-lane (All Nearby) presentations.

#### Scenario: Only the window is built

- **WHEN** a timetable with 225 loaded dates is first displayed or restored on re-entry
- **THEN** at most 24 date groups SHALL be built
- **AND** the number built SHALL NOT depend on how many dates are loaded

#### Scenario: Scrolling down reaches every later date

- **WHEN** the fan scrolls toward the last built date
- **THEN** later dates SHALL be added before the fan reaches the end of the
  built content
- **AND** continuing to scroll SHALL reach the last loaded date

#### Scenario: Scrolling up from a restored date reaches earlier dates without a jump

- **WHEN** the timetable was restored deep in the list and the fan scrolls up
- **THEN** earlier dates SHALL be added above
- **AND** the date the fan is looking at SHALL stay where it is on screen while
  they are added

#### Scenario: Lanes stay aligned in every built group

- **WHEN** any date group is built, including one added while scrolling
- **THEN** its lane columns SHALL align with the stage header's columns
- **AND** this SHALL hold in both the three-lane and the two-lane presentations

## MODIFIED Requirements

### Requirement: Timetable rendering cost is bounded and must not dominate the main thread

Displaying the dashboard timetable — on first navigation and on tab-switch
re-entry — SHALL cost main-thread time bounded by the dates in view, not by the
number of loaded dates. This covers both building the timetable (creating and
binding the date groups and cards) and the browser's style, layout and paint
work for it. Rendering cost is dominated by main-thread work, not by network or
backend latency, so this contract constrains main-thread rendering only; the
backend/RPC path is out of scope.

Measurements are taken on the reference profile — a mid-tier mobile device (e.g.
Pixel 8) or a desktop emulating it with 4× CPU throttling — against a recorded
pre-change baseline, on an account whose timetable holds at least 200 dates.

#### Scenario: Tab-switch re-entry does not freeze on rendering

- **WHEN** an authenticated fan with a populated timetable taps the dashboard
  navigation tab from another tab
- **THEN** the tap's Interaction to Next Paint (INP), measured on the reference
  profile, SHALL be at most 200 ms
- **AND** the timetable content SHALL appear in that same next paint, with no
  skeleton shown in between

#### Scenario: First dashboard load render cost is reduced

- **WHEN** an authenticated fan with a populated timetable loads the dashboard
- **THEN** the main-thread time to render the timetable once its data arrives,
  measured on the reference profile, SHALL be at most 200 ms

#### Scenario: Off-screen timetable content is not styled or laid out eagerly

- **WHEN** the timetable holds more dates than fit in the viewport
- **THEN** dates outside the rendered window SHALL contribute no building,
  style, layout or paint work to the entry or re-entry interaction

#### Scenario: Viewport-scoping off-screen content does not regress sticky headers or shift layout

- **WHEN** a fan scrolls across multiple date groups, including groups added to
  the window while scrolling
- **THEN** the date separator's sticky behavior is intentional and consistent
  across groups (either it persists at the top or it hands off at each group
  boundary — not a mix), and no cumulative layout shift is introduced (CLS stays 0)
  as groups are added

### Requirement: Re-entry restores the date the fan was looking at

On re-entry to a timetable the fan has already seen, the cached content SHALL be
restored showing the same date group the fan left it on, at any scroll depth.

The position SHALL be remembered as the date it identifies, not as a pixel
offset, because the dates above it are not all built after the trip and a pixel
offset would denote a different place. The window SHALL be built around the
remembered date, so the date exists when the view is positioned on it and the
fan never sees the timetable at the top first.

A date that is no longer in the list SHALL leave the window at the nearest
later date rather than fail.

#### Scenario: Re-entry restores the same date, at any depth

- **WHEN** a fan scrolls deep into the timetable, navigates to another tab, and
  returns
- **THEN** the first paint of the timetable SHALL show the same date group it
  showed when they left
- **AND** this SHALL hold as far down the timetable as the content goes, not only
  near the top

#### Scenario: The anchored date is gone

- **WHEN** the timetable is restored but a background refresh has dropped the
  date the fan left it on
- **THEN** the view SHALL show the nearest later date that remains
- **AND** SHALL NOT reset to the top or fail

### Requirement: Page identity paints independent of the timetable render

On dashboard tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — SHALL NOT be held back by an unbounded timetable
render. The re-entry render SHALL be bounded by the rendered window, so that page
identity and the restored timetable appear in the tap's next paint within the
interaction budget, whatever the number of loaded dates. Reflecting timetable
render state SHALL NOT be performed in a pre-activation route lifecycle hook.
Re-entry SHALL NOT lose the background refresh, the data-ready
celebration/onboarding latch, or an in-flight deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the dashboard navigation tab from another tab
- **THEN** the header title, the active tab and the restored timetable SHALL
  appear in the tap's next paint, with the tap's Interaction to Next Paint at
  most 200 ms on the reference profile
- **AND** the render work for that interaction SHALL be bounded by the rendered
  window, not by the full set of loaded date groups

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is reflected from the component lifecycle
- **THEN** the background refresh SHALL still fetch and swap in fresh data
- **AND** the data-ready celebration / onboarding-completion latch SHALL still
  fire once when due, and a pending `/concerts/:id` deep-link SHALL still open
  the detail sheet

## REMOVED Requirements

### Requirement: Timetable rendering is scoped to the viewport
**Reason**: Viewport scoping skipped style, layout and paint for off-screen dates but still built every date group and card, so the render grew with the number of loaded dates. Dates outside the view are now not built at all.
**Migration**: Replaced by "The timetable renders a window of dates around the fan", which keeps the lane-alignment scenario.
