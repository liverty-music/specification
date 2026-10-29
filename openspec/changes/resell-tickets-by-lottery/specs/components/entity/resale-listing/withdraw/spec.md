# Spec Delta

## ADDED Requirements

### Requirement: Withdraw only a free listing

Withdraw SHALL take a ResaleListing and a time. When the listing is free for a draw at that time, Withdraw SHALL make it Withdrawn with that withdraw time. When it is already Withdrawn, it SHALL change nothing. Otherwise, when it is allocated to a Won ResaleEntry, Sold, Cancelled or expired, it SHALL fail with FailedPrecondition and change nothing. Checking and withdrawing SHALL be one indivisible step with recording a draw, so a listing is never both withdrawn and allocated. It SHALL fail with NotFound when no listing has the id.

#### Scenario: Nobody is buying it
- **WHEN** a listing free for a draw is withdrawn
- **THEN** it is Withdrawn

#### Scenario: Another fan won it
- **WHEN** the listing is allocated to another fan's Won entry that is being charged
- **THEN** Withdraw fails with FailedPrecondition and the listing stays Listed

#### Scenario: Withdraw and draw at the same moment
- **WHEN** a Withdraw and a draw's ResaleEntry.PersistDrawOutcome allocating the same listing run at the same time
- **THEN** either the listing is Withdrawn and the draw records nothing, or the listing is allocated and Withdraw fails with FailedPrecondition

#### Scenario: Already sold
- **WHEN** a Sold listing is withdrawn
- **THEN** Withdraw fails with FailedPrecondition

#### Scenario: Withdrawn twice
- **WHEN** a Withdrawn listing is withdrawn again
- **THEN** nothing changes

## REMOVED Requirements

### Requirement: Withdraw an open listing

**Reason**: A listing allocated to a Won ResaleEntry is being bought and cannot be withdrawn.
**Migration**: See "Withdraw only a free listing".
