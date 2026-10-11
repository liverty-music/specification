# components/entity/reservation/revert-commit Specification

## Purpose
Gives a Committed Reservation's tickets back to the sale when its card can no longer be charged.

## Requirements

### Requirement: Revert only an uncharged commit

RevertCommit SHALL make a Committed Reservation without a capture time Released and take its count off the sale's sold count, in one indivisible step, keeping its committed time so it stays known that it was committed. It SHALL fail with FailedPrecondition, changing nothing, when the Reservation has a capture time. A Reservation that is not Committed SHALL be left unchanged. It SHALL fail with NotFound when no Reservation has the id.

#### Scenario: Card closed after the commit

- **WHEN** a Committed, uncharged Reservation for 2 committed at 18:10 is reverted
- **THEN** it is Released with committed time 18:10, and the sale's sold count falls by 2

#### Scenario: Already charged

- **WHEN** a Committed Reservation with a capture time is reverted
- **THEN** RevertCommit fails with FailedPrecondition and nothing changes
