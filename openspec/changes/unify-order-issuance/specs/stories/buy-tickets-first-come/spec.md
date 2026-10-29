## MODIFIED Requirements

### Requirement: Fan buys tickets

After an Organizer adds a SeatType to a Series with SeatTypeUseCase.Create, stocks it for a published event with TicketStockUseCase.Create and creates a FirstCome TicketSale naming the event with TicketSaleUseCase.Create, a signed-in fan SHALL be able to:
1. hold tickets of that TicketStock with CheckoutUseCase.Start;
2. authorize their card with CheckoutUseCase.AuthorizeCard, giving their full name and phone number, and complete card authentication;
3. place the order with OrderUseCase.Place.

Their Tickets SHALL then be in TicketUseCase.List, and a confirmation email SHALL arrive within 5 minutes.

#### Scenario: Two tickets bought

- **WHEN** a fan buys 2 tickets of a SeatType priced 3000 yen from a TicketStock of 150
- **THEN** they are charged 6000 yen, hold 2 Issued Tickets of that SeatType for the event, their ticket journey for the event is Paid, and they receive one confirmation email
