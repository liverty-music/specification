# components/entity/resale-listing/withdraw Specification

## Purpose
Withdraws a fan's ResaleListing that no Checkout holds, so its Ticket is no longer for sale.

## Requirements

### Requirement: Withdraw an open listing

Withdraw SHALL take a ResaleListing and a time. When the listing is open at that time, Withdraw SHALL make it Withdrawn with that withdraw time. When it is already Withdrawn, it SHALL change nothing. Otherwise, when it is Sold, Cancelled or expired, it SHALL fail with FailedPrecondition and change nothing. It SHALL fail with NotFound when no listing has the id.

#### Scenario: Fan withdraws an open listing
- **WHEN** an open listing is withdrawn
- **THEN** it is Withdrawn

#### Scenario: Already sold
- **WHEN** a Sold listing is withdrawn
- **THEN** Withdraw fails with FailedPrecondition

#### Scenario: Withdrawn twice
- **WHEN** a Withdrawn listing is withdrawn again
- **THEN** nothing changes
