# Spec Delta

## ADDED Requirements

### Requirement: Caller's entries in a sale

ListByTicketType SHALL take a Lottery TicketSale and the calling fan and return the fan's entries in it, each with its Order's TicketStock and ticket count, from LotteryEntry.ListByTicketTypeAndUser; a fan has at most one for each event the sale names. It SHALL return an empty list when the fan has none, and SHALL fail with NotFound when the sale does not exist (TicketSale.Get).

#### Scenario: Entered entry
- **WHEN** the fan has an Entered entry in the sale for 2 S席 tickets
- **THEN** it is returned with the S席 stock and 2 tickets

#### Scenario: Fan won
- **WHEN** the draw has run and the fan's entry is Won
- **THEN** the returned entry is Won

#### Scenario: Fan lost
- **WHEN** the draw has run and the fan's entry is Lost
- **THEN** the returned entry is Lost

#### Scenario: Never entered
- **WHEN** the fan has no entry in the sale
- **THEN** an empty list is returned

## REMOVED Requirements

### Requirement: Caller's entries for a ticket type

**Reason**: A fan enters a sale once for each event, for one TicketStock of it; there is no TicketType.
**Migration**: See "Caller's entries in a sale".
