# Spec Delta

## MODIFIED Requirements

### Requirement: Release recorded once

MarkReleased SHALL set a Held Settlement to Released with the given charge reference and released time, and record each given split's payout reference, all together or not at all. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Held or no Settlement has the id.

#### Scenario: Held settlement released

- **WHEN** MarkReleased is called for a Held Settlement
- **THEN** it is Released with its charge reference, released time and payout references

#### Scenario: Already released or reversed

- **WHEN** the Settlement is Released or Reversed
- **THEN** MarkReleased fails with FailedPrecondition and changes nothing

#### Scenario: Unknown id

- **WHEN** no Settlement has the id
- **THEN** MarkReleased fails with FailedPrecondition

#### Scenario: Failure changes nothing

- **WHEN** recording any split's payout reference fails
- **THEN** the Settlement stays Held, with no charge reference or released time recorded and no split's payout reference recorded
