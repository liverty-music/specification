# Delta for coach-mark

## MODIFIED Requirements

### Requirement: One non-blocking coach mark rendered by the screen that uses it

The coach mark SHALL be a single, transient, non-blocking hint. At most one coach mark SHALL be shown at a time. It SHALL NOT lock page scroll and SHALL NOT block interaction with the rest of the page. The screen that uses a coach mark SHALL render it within that screen; today the only such screen is Welcome, for its demo timetable. Discovery, the Timetable, the concert sheet and My Artists point fans to features with guide moments (the guide-moment surface), which dim nothing, and never with a coach mark. The coach mark SHALL close when the user taps its target, taps outside it, or leaves the screen.

#### Scenario: Coach mark does not block the rest of the page

- **WHEN** a coach mark is shown
- **THEN** the page outside the highlighted target remains interactive
- **AND** page scroll is not locked

#### Scenario: Only the Welcome demo shows a coach mark

- **WHEN** a fan uses Discovery, the Timetable or My Artists
- **THEN** no coach mark is shown on those screens, and no part of those screens is dimmed by a guide
- **WHEN** a visitor reaches the interactive timetable of the Welcome demo
- **THEN** the Welcome screen may show its coach mark, and at most one coach mark is shown

#### Scenario: Coach mark closes on any tap or on leaving the screen

- **WHEN** the user taps the coach mark target, OR taps outside it, OR leaves the screen
- **THEN** the coach mark closes and its spotlight, message and dimmed layer are removed
