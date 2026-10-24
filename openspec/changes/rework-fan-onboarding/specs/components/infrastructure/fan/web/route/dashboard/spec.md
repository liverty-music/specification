## MODIFIED Requirements

### Requirement: Data-ready side effects gate on observed data arrival
Side effects that must only run once a route's data is genuinely present (e.g. the Dashboard post-signup/guest celebration and the onboarding-completion latch) SHALL be triggered by observing the arrival of that data, NOT by relying on the router having awaited the fetch before the view attaches. Every arrival of the timetable SHALL count as an arrival, including one served from concert data already fetched earlier in the same session.

#### Scenario: Celebration fires only once the timetable is real
- **WHEN** the Dashboard loads data non-blocking and the data arrives after the view has attached
- **THEN** the celebration decision SHALL be evaluated when the loaded data is observed to be present
- **AND** the celebration SHALL NOT be presented over a still-loading (spinner) timetable

#### Scenario: Completion latch waits for engagement data
- **WHEN** the onboarding-completion latch condition depends on loaded follow/engagement data
- **THEN** the latch SHALL be evaluated upon observed arrival of that data
- **AND** it SHALL NOT short-circuit on not-yet-loaded state when the route attaches

#### Scenario: Home area chosen on arrival, timetable served from session data
- **WHEN** a guest in onboarding who follows at least one artist arrives at the Dashboard without a home area
- **AND** the guest chooses a home area in the home-area sheet
- **AND** the timetable then appears from concert data already fetched earlier in the same session
- **THEN** the celebration decision SHALL be evaluated exactly once
- **AND** the onboarding-completion latch SHALL be evaluated exactly once
