## MODIFIED Requirements

### Requirement: A winning fan receives tickets

After an Organizer stocks a SeatType for a published event with TicketStockUseCase.Create and creates a Lottery TicketSale naming the event with TicketSaleUseCase.Create, a fan SHALL be able to authorize their card for a ticket count of that TicketStock with LotteryEntryUseCase.AuthorizeCard, complete card authentication and confirm the entry with LotteryEntryUseCase.Confirm while the window is open. After the window closes, the platform SHALL draw the sale and tell each fan the result. When the fan's entry wins, the fan SHALL be charged, receive the confirmation email and a push notification saying the entry won, find the entry Won with LotteryEntryUseCase.ListByTicketType and find its Tickets with TicketUseCase.List.

#### Scenario: Demand within quantity
- **WHEN** a fan enters 2 tickets for a TicketStock of 100 tickets whose SeatType is priced 8000 yen, and the window closes with fewer than 100 tickets requested
- **THEN** after the draw the fan's entry is Won, 16000 yen is charged, the fan receives one confirmation email saying the entry won, and the fan holds 2 Issued Tickets for the event, their faces show the fan's full name and phone number, and their ticket journey for the event is Paid

### Requirement: A losing fan is never charged

A fan whose entry is not admitted SHALL be told by email and push notification that the entry lost, SHALL find it Lost with LotteryEntryUseCase.ListByTicketType and SHALL NOT be charged.

#### Scenario: Oversubscribed sale
- **WHEN** a TicketStock with 4 tickets remaining closes with entries for 12 tickets and the fan's entry is not admitted
- **THEN** the fan's entry is Lost, its card authorization is released, the fan receives one email saying the entry lost and nothing is charged, and the fan holds no Ticket for the event

## ADDED Requirements

### Requirement: A draw that stops midway keeps its winners

When the platform stops while it draws a sale or charges its winners, the draw SHALL resume with the same winners: every Won fan SHALL be charged once and receive their Tickets, and no fan SHALL be charged without Tickets.

#### Scenario: Stopped after the first charge
- **WHEN** a sale's TicketStock with 4 tickets remaining closes with entries for 2, 2 and 3 tickets, the platform stops after charging one of the two winners, and starts again
- **THEN** the same two entries are Won, each winner is charged once and holds 2 Issued Tickets, and the 3-ticket entry is Lost and never charged

### Requirement: A winner whose card can no longer be charged loses

When a Won fan's card authorization can no longer be charged, the fan's entry SHALL become Lost, the fan SHALL be told by email that the win was cancelled because the card could not be charged, and the fan SHALL NOT be charged or hold any Ticket for it. Its tickets stay unallocated.

#### Scenario: Card closed before the charge
- **WHEN** a fan's entry wins and the fan's card was closed before the charge
- **THEN** the fan's entry is Lost, nothing is charged, the fan holds no Ticket for the event, and the fan receives one email saying the win was cancelled because the card could not be charged
