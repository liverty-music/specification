# Settlement.MarkReleased

## Purpose

Records that a Held Settlement was paid out: its charge reference, released time and each split's payout reference.

## Requirements

### Requirement: Release recorded once

MarkReleased SHALL set a Held Settlement to Released with the given charge reference and released time, then record each given split's payout reference. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Held or no Settlement has the id.

#### Scenario: Held settlement released

- **WHEN** MarkReleased is called for a Held Settlement
- **THEN** it is Released with its charge reference, released time and payout references

#### Scenario: Already released or reversed

- **WHEN** the Settlement is Released or Reversed
- **THEN** MarkReleased fails with FailedPrecondition and changes nothing

#### Scenario: Unknown id

- **WHEN** no Settlement has the id
- **THEN** MarkReleased fails with FailedPrecondition
