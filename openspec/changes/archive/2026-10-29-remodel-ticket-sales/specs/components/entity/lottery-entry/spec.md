# Spec Delta

## ADDED Requirements

### Requirement: Sale of an entry

A LotteryEntry SHALL belong to a Lottery sale that names its Order's event.

#### Scenario: Lottery sale of the event
- **WHEN** a LotteryEntry belongs to a Lottery sale that names the event of its Order's TicketStock
- **THEN** it is valid

#### Scenario: First-come sale
- **WHEN** a LotteryEntry belongs to a FirstCome sale
- **THEN** it is invalid

## MODIFIED Requirements

### Requirement: A new entry is Entered

A LotteryEntry SHALL be created in state Entered, without a draw position, for an Order that has its card authorization.

#### Scenario: New entry
- **WHEN** a LotteryEntry is created
- **THEN** its state is Entered, its Order has its card authorization and it has no draw position

## REMOVED Requirements

### Requirement: Ticket count fits the ticket type

**Reason**: The ticket count is on the entry's Order and fits its event's per-account limit.
**Migration**: See components/entity/order "Ticket count fits the event".
