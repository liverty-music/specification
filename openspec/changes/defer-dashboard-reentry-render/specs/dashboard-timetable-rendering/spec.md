## ADDED Requirements

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

### Requirement: Entrance motion is limited to first load

Cards SHALL animate into view only on a genuine first load of the timetable. On
re-entry to a timetable the fan has already seen, the cached content SHALL be
restored without entrance motion and at the scroll position it had when the fan
left. Restoring a scroll position SHALL be clamped to the restored content's
extent. When the fan prefers reduced motion, entrance animation SHALL be
suppressed without reintroducing a blocking render.

#### Scenario: Cold load animates, re-entry does not

- **WHEN** a fan opens the dashboard for the first time in a session
- **THEN** the cards SHALL animate in as the data arrives
- **WHEN** the same fan leaves and returns to the dashboard
- **THEN** the cached timetable SHALL appear without entrance motion

#### Scenario: Re-entry restores the previous scroll position

- **WHEN** a fan scrolls deep into the timetable, navigates to another tab, and
  returns
- **THEN** the timetable SHALL be restored at the scroll position it had when
  they left
- **AND** if the restored content is shorter than that position, the view SHALL
  clamp to the end of the content rather than failing

### Requirement: Page identity paints independent of the timetable render

On dashboard tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — SHALL be painted at navigation intent, independent of
and ahead of the timetable's render. Reflecting timetable render state SHALL NOT
be performed in a pre-activation route lifecycle hook, so it cannot be folded
into the component's first render and starve the page-identity paint. Deferring
the timetable render SHALL NOT lose the background refresh, the data-ready
celebration/onboarding latch, or an in-flight deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the dashboard navigation tab from another tab
- **THEN** the shell header title and the active bottom-nav tab SHALL switch to
  the dashboard's identity before the timetable's render work runs
- **AND** the tap's Interaction to Next Paint SHALL be substantially lower than
  the pre-change baseline, with the shell interactive while the timetable fills

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is reflected after the component's first
  render
- **THEN** the background refresh SHALL still fetch and swap in fresh data
- **AND** the data-ready celebration / onboarding-completion latch SHALL still
  fire once when due, and a pending `/concerts/:id` deep-link SHALL still open
  the detail sheet
