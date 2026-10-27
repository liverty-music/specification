## MODIFIED Requirements

### Requirement: Fan buys tickets

After an Organizer creates a FirstCome TicketSale with a TicketType for a published event with TicketSaleUseCase.Create, a signed-in fan SHALL be able to:
1. hold tickets of that TicketType with CheckoutUseCase.Start;
2. authorize their card with CheckoutUseCase.AuthorizeCard, giving their full name and phone number, and complete card authentication;
3. place the order with OrderUseCase.Place.

Their Tickets SHALL then be in TicketUseCase.List, and a confirmation email SHALL arrive within 5 minutes.

#### Scenario: Two tickets bought

- **WHEN** a fan buys 2 tickets of 3000 yen from a TicketType of 150
- **THEN** they are charged 6000 yen, hold 2 Issued Tickets for the event, their ticket journey for the event is Paid, and they receive one confirmation email
