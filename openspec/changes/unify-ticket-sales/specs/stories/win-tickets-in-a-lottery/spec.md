# Spec Delta

## MODIFIED Requirements

### Requirement: The Organizer's payout readiness never blocks the sale

Fans SHALL be able to enter, win and receive tickets for an Organizer's lottery whatever the state of the Organizer's payout account; only the Organizer's payout waits until the account is Active, as SettlementUseCase.ReleaseDueSettlements states.

#### Scenario: Organizer still in identity check
- **WHEN** an Organizer whose payout account is Pending runs a lottery and a fan's entry wins
- **THEN** the fan is charged and holds Issued Tickets, while the Organizer's payout stays Held until the account is Active

## REMOVED Requirements

### Requirement: Winning fan receives tickets
**Reason**: Renamed with its scenario "Demand within capacity", because a TicketType has a quantity, not a capacity (design D17).
**Migration**: Replaced by "A winning fan receives tickets" with the scenario "Demand within quantity".

### Requirement: Losing fan is never charged
**Reason**: Renamed with its scenario "Oversubscribed phase", because the sale is a TicketSale, not a phase (design D17).
**Migration**: Replaced by "A losing fan is never charged" with the scenario "Oversubscribed sale".

### Requirement: Withdrawing before the draw
**Reason**: Renamed with its scenario "Withdraw and re-apply", because a fan enters a lottery rather than applies (design D17).
**Migration**: Replaced by "A fan can withdraw before the draw" with the scenario "Withdraw and enter again".

## ADDED Requirements

### Requirement: A winning fan receives tickets

After an Organizer creates a Lottery TicketSale for a published event with TicketSaleUseCase.Create, a fan SHALL be able to start an entry for the event's TicketType with LotteryEntryUseCase.Start, authorize their card with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open, and — when their entry wins — find it Won with LotteryEntryUseCase.ListOwnByTicketType within 1 minute after the window closes and find its Tickets with TicketUseCase.List within 1 more minute.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketType of 100 tickets priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 1 minute the fan's entry is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

### Requirement: A losing fan is never charged

A fan whose entry is not admitted SHALL find it Lost with LotteryEntryUseCase.ListOwnByTicketType and SHALL NOT be charged.

#### Scenario: Oversubscribed sale
- **WHEN** a TicketType of 4 tickets closes with entries for 12 tickets and the fan's entry is not admitted
- **THEN** the fan's entry is Lost, its card authorization is released, and the fan holds no Ticket for the event

### Requirement: A fan can withdraw before the draw

A fan SHALL be able to withdraw with LotteryEntryUseCase.WithdrawEntry before the draw and enter again while the window is open. A Draft the fan never confirmed SHALL take no part in the draw, and its card authorization SHALL be released at the draw.

#### Scenario: Withdraw and enter again
- **WHEN** a fan withdraws their entry while the window is open and enters again with a new card authorization
- **THEN** the first card authorization is released and only the new entry takes part in the draw

#### Scenario: Entry left unconfirmed
- **WHEN** a fan authorizes their card but leaves before confirming, and the window closes
- **THEN** the card authorization is released at the draw, the fan is never charged, and the entry is Withdrawn

### Requirement: A presale and a general sale share the per-account limit

When an event has a presale and a later general sale, a fan who won tickets in the presale SHALL be able to enter the general sale only for the tickets still under the general sale's per-account limit.

#### Scenario: Presale winner at the limit
- **WHEN** a fan won 4 tickets in an event's presale and the event's general sale has a per-account limit of 4
- **THEN** the fan's entry into the general sale is refused and the fan still holds 4 Tickets

#### Scenario: Presale winner below the limit
- **WHEN** a fan won 2 tickets in the presale and enters 2 tickets in a general sale with a per-account limit of 4
- **THEN** the entry is made
