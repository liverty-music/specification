# Spec Delta

## MODIFIED Requirements

### Requirement: A winning fan receives tickets

After an Organizer stocks a SeatType for a published event with TicketStockUseCase.Create and creates a Lottery TicketSale naming the event with TicketSaleUseCase.Create, a fan SHALL be able to authorize their card for a ticket count of that TicketStock with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open, and — when their entry wins — find it Won with LotteryEntryUseCase.ListBySale within 2 minutes after the window closes and find its Tickets with TicketUseCase.List within 1 more minute.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketStock of 100 tickets whose SeatType is priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** within 2 minutes the fan's entry is Won and 16000 yen is charged, and within 1 more minute the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

### Requirement: A losing fan is never charged

A fan whose entry is not admitted SHALL find it Lost with LotteryEntryUseCase.ListBySale and SHALL NOT be charged.

#### Scenario: Oversubscribed sale
- **WHEN** a TicketStock with 4 tickets remaining closes with entries for 12 tickets and the fan's entry is not admitted
- **THEN** the fan's entry is Lost, its card authorization is released, and the fan holds no Ticket for the event
