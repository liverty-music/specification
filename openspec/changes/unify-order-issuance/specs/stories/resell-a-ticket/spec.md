## MODIFIED Requirements

### Requirement: A ticket is resold and its fan refunded

After a FirstCome TicketType sold out, a signed-in fan holding Issued Tickets of it SHALL be able to list one with ResaleListingUseCase.Create. Another signed-in fan SHALL then be able to buy it through CheckoutUseCase.Start, CheckoutUseCase.AuthorizeCard and OrderUseCase.Place, as for a first-come purchase. The first fan's listed Ticket SHALL then be Voided, the other fan SHALL hold a new Issued Ticket for the event in TicketUseCase.List and receive the purchase confirmation email, and within 2 minutes of the purchase the first fan SHALL be refunded the refund amount and receive the sold email.

#### Scenario: One of two tickets resold
- **WHEN** a fan holding 2 tickets of 5000 yen for a sold-out event lists one, and another fan buys a resale ticket
- **THEN** the other fan is charged 5000 yen and holds 1 Issued Ticket, the first fan holds 1 Issued and 1 Voided Ticket, is refunded 4500 yen within 2 minutes and receives one sold email, and ResaleListingUseCase.List shows the listing Sold and refunded
