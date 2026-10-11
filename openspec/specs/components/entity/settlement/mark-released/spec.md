# Settlement.MarkReleased

## Purpose

Records that a Held Settlement was paid out: its provider charge ID, release time and each split's provider payout ID.

## Requirements

### Requirement: Release recorded once

MarkReleased SHALL set a Held Settlement to Released with the given provider charge ID and release time, and record each given split's provider payout ID, all together or not at all. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Held or no Settlement has the id.

#### Scenario: Held settlement released

- **WHEN** MarkReleased is called for a Held Settlement
- **THEN** it is Released with its provider charge ID, release time and provider payout IDs

#### Scenario: Already released or reversed

- **WHEN** the Settlement is Released or Reversed
- **THEN** MarkReleased fails with FailedPrecondition and changes nothing

#### Scenario: Unknown id

- **WHEN** no Settlement has the id
- **THEN** MarkReleased fails with FailedPrecondition

#### Scenario: Failure changes nothing

- **WHEN** recording any split's provider payout ID fails
- **THEN** the Settlement stays Held, with no provider charge ID or release time recorded and no split's provider payout ID recorded

