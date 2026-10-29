# Spec Delta

## ADDED Requirements

### Requirement: One seat type per account and event

A fan SHALL hold or apply for tickets of only one SeatType for an event, across every sale of the event, and SHALL enter one Lottery sale at most once for each event.

#### Scenario: Presale winner picks another seat type
- **WHEN** a fan won 2 S席 tickets in an event's presale and enters A席 in the general sale
- **THEN** the entry is refused and the fan still holds 2 S席 Tickets

#### Scenario: Second entry into the same sale
- **WHEN** a fan entered a lottery sale for S席 and tries to enter the same sale again
- **THEN** the second entry is refused

## MODIFIED Requirements

### Requirement: A winning fan receives tickets

After an Organizer stocks a SeatType for a published event with TicketStockUseCase.Create and creates a Lottery TicketSale naming the event with TicketSaleUseCase.Create, a fan SHALL be able to authorize their card for a ticket count of that TicketStock with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open, and — when their entry wins — find it Won with LotteryEntryUseCase.ListByTicketType within 2 minutes after the window closes and find its Tickets with TicketUseCase.List within 1 more minute.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketStock of 100 tickets whose SeatType is priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 2 minutes the fan's entry is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

### Requirement: A losing fan is never charged

A fan whose entry is not admitted SHALL find it Lost with LotteryEntryUseCase.ListByTicketType and SHALL NOT be charged.

#### Scenario: Oversubscribed sale
- **WHEN** a TicketStock with 4 tickets remaining closes with entries for 12 tickets and the fan's entry is not admitted
- **THEN** the fan's entry is Lost, its card authorization is released, and the fan holds no Ticket for the event

### Requirement: A presale and a general sale share the per-account limit

When an event has a presale and a later general sale, a fan who won tickets in the presale SHALL be able to enter the general sale only for the tickets still under the event's per-account limit.

#### Scenario: Presale winner at the limit
- **WHEN** a fan won 4 tickets in an event's presale and the event's per-account limit is 4
- **THEN** the fan's entry into the general sale is refused and the fan still holds 4 Tickets

#### Scenario: Presale winner below the limit
- **WHEN** a fan won 2 S席 tickets in the presale and enters 2 S席 tickets in the general sale of an event with a per-account limit of 4
- **THEN** the entry is made
