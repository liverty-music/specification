# Spec Delta

## MODIFIED Requirements

### Requirement: Release eligibility

A Settlement SHALL be eligible for release at an instant, given its event's publish state, its event's current start time, a dispute buffer and its Order's Disputes, only when the event is not CANCELLED, the start time is known, the instant is after the start time plus the buffer, and the Order has no open and no unsettled Dispute (Dispute, "Unsettled outcome"). A Settlement of a CANCELLED Event is therefore never eligible for release.

#### Scenario: Start time unknown

- **WHEN** the event has no start time
- **THEN** the Settlement is not eligible for release

#### Scenario: Buffer not yet elapsed

- **WHEN** the instant is before the start time plus the buffer
- **THEN** the Settlement is not eligible for release

#### Scenario: Buffer elapsed

- **WHEN** the event is PUBLISHED, the instant is after the start time plus the buffer and the Order has no open Dispute
- **THEN** the Settlement is eligible for release

#### Scenario: Cancelled event

- **WHEN** the event is CANCELLED and the instant is after the start time plus the buffer
- **THEN** the Settlement is not eligible for release

#### Scenario: Payment disputed

- **WHEN** the buffer elapsed and the Order has a Contested Dispute
- **THEN** the Settlement is not eligible for release

#### Scenario: Lost dispute not yet settled

- **WHEN** the buffer elapsed and the Order has a Lost Dispute with no settle time
- **THEN** the Settlement is not eligible for release

### Requirement: Released only from Held

A Settlement SHALL be claimed for release only while Held, and recorded Released only while Releasing; a Released or Reversed Settlement is never released again. A Releasing Settlement SHALL become Released when its release is recorded, or Held again when its payout could not start; it SHALL NOT become Reversed until its release has ended.

#### Scenario: Reversed settlement

- **WHEN** the status is Reversed
- **THEN** the Settlement is not releasable

#### Scenario: Releasing settlement

- **WHEN** the status is Releasing
- **THEN** it cannot be claimed again and cannot become Reversed
