# components/entity/resale-listing/withdraw Specification

## Purpose
Withdraws a fan's ResaleListing that no Checkout holds, so its Ticket is no longer for sale.

## Requirements

### Requirement: Withdraw only a free listing

Withdraw SHALL take a ResaleListing and a time. When the listing is free at that time, Withdraw SHALL make it Withdrawn with that withdraw time. When it is already Withdrawn, it SHALL change nothing. Otherwise, when it is held by a holding or Committed Checkout, Sold, Cancelled or expired, it SHALL fail with FailedPrecondition and change nothing. Checking and withdrawing SHALL be one indivisible step with holding the listing, so a listing is never both withdrawn and held. It SHALL fail with NotFound when no listing has the id.

#### Scenario: Nobody is buying it
- **WHEN** a free listing is withdrawn
- **THEN** it is Withdrawn

#### Scenario: Another fan is checking out
- **WHEN** the listing is held by another fan's holding Checkout
- **THEN** Withdraw fails with FailedPrecondition and the listing stays Listed

#### Scenario: Withdraw and hold at the same moment
- **WHEN** a Withdraw and another fan's Checkout.GetOrCreateHeld for the same free listing run at the same time
- **THEN** either the listing is Withdrawn and the Checkout does not hold it, or the Checkout holds it and Withdraw fails with FailedPrecondition

#### Scenario: Already sold
- **WHEN** a Sold listing is withdrawn
- **THEN** Withdraw fails with FailedPrecondition

#### Scenario: Withdrawn twice
- **WHEN** a Withdrawn listing is withdrawn again
- **THEN** nothing changes
