## ADDED Requirements

### Requirement: Which journeys the platform and the app may replace

A status set by inference SHALL replace no journey: the app records it only when the fan has no journey for the event. Applied set by the platform SHALL replace a journey at Tracking, Applied or Lost, whoever set it, and SHALL NOT replace a journey at Unpaid or Paid, because the fan already has a ticket for the event. A status the fan sets replaces any journey (components/entity/ticket-journey/upsert).

#### Scenario: Inference over an existing journey

- **WHEN** the fan's journey is Lost set by the fan and the app infers Tracking
- **THEN** the journey is not replaceable

#### Scenario: Entry after a lost presale

- **WHEN** the fan's journey is Lost set by the fan and the platform records Applied for a new lottery entry
- **THEN** the journey is replaceable

#### Scenario: Entry announced after the purchase

- **WHEN** the fan's journey is Paid set by the platform and the platform records Applied
- **THEN** the journey is not replaceable
