## MODIFIED Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks. Each phase waits for a user tap to advance. The HOME phase pauses to collect the user's 居住エリア selection before displaying the dynamic coach mark text.

#### Scenario: Lane introduction begins after Dashboard load

- **WHEN** the user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **AND** `ConcertService/ListWithProximity` has returned 1 or more date groups
- **THEN** the system SHALL begin the lane introduction sequence
- **AND** the lane intro SHALL start regardless of `showCelebration` state (celebration is not set until lane intro completes)
- **AND** scrolling SHALL be disabled during the entire sequence
- **AND** blocker divs SHALL be active

#### Scenario: Lane introduction skipped when no concert data

- **WHEN** the Dashboard page loads
- **AND** `ConcertService/ListWithProximity` has returned 0 date groups
- **THEN** the system SHALL NOT begin the lane introduction sequence
- **AND** the system SHALL proceed directly to the Celebration Overlay
- **AND** the system SHALL log a warning: "No concert data available, skipping lane intro"

#### Scenario: Transition to Celebration after AWAY phase

- **WHEN** the AWAY phase tap is received
- **THEN** the system SHALL call `completeLaneIntro()`
- **AND** `completeLaneIntro()` SHALL set `showCelebration = true`
- **AND** `showCelebration` SHALL NOT be set in `loading()` or any earlier lifecycle hook
