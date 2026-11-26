## MODIFIED Requirements

### Requirement: Release eligibility

A Settlement SHALL be eligible for release at an instant, given its event's publish state, its event's current start time and a dispute buffer, only when the event is not CANCELLED, the start time is known and the instant is after the start time plus the buffer. A Settlement of a CANCELLED Event is therefore never eligible for release.

#### Scenario: Start time unknown

- **WHEN** the event has no start time
- **THEN** the Settlement is not eligible for release

#### Scenario: Buffer not yet elapsed

- **WHEN** the instant is before the start time plus the buffer
- **THEN** the Settlement is not eligible for release

#### Scenario: Buffer elapsed

- **WHEN** the event is PUBLISHED and the instant is after the start time plus the buffer
- **THEN** the Settlement is eligible for release

#### Scenario: Cancelled event

- **WHEN** the event is CANCELLED and the instant is after the start time plus the buffer
- **THEN** the Settlement is not eligible for release
