## Purpose

A fan who bought first-come tickets and cannot attend lists one through official resale (公式リセール) after the sale sold out; another fan buys it at face value through the usual checkout, receives a new ticket in their own name, and the first fan is refunded the face value minus the 10% resale fee, while the Organizer is paid once for the seat.

## ADDED Requirements

### Requirement: A ticket is resold and its fan refunded

After a FirstCome TicketType sold out, a signed-in fan holding Issued Tickets of it SHALL be able to list one with ResaleListingUseCase.Create. Another signed-in fan SHALL then be able to buy it through CheckoutUseCase.Start, CheckoutUseCase.AuthorizeCard and OrderUseCase.IssueFromCheckout, as for a first-come purchase. The first fan's listed Ticket SHALL then be Voided, the other fan SHALL hold a new Issued Ticket for the event in TicketUseCase.List and receive the purchase confirmation email, and within 2 minutes of the purchase the first fan SHALL be refunded the refund amount and receive the sold email.

#### Scenario: One of two tickets resold
- **WHEN** a fan holding 2 tickets of 5000 yen for a sold-out event lists one, and another fan buys a resale ticket
- **THEN** the other fan is charged 5000 yen and holds 1 Issued Ticket, the first fan holds 1 Issued and 1 Voided Ticket, is refunded 4500 yen within 2 minutes and receives one sold email, and ResaleListingUseCase.List shows the listing Sold and refunded

### Requirement: The Organizer is paid once per seat

A resale SHALL leave the Organizer's total payout for the event as it was before, to within 1 yen per resold ticket from rounding.

#### Scenario: Payout after a resale
- **WHEN** an Organizer at a 5% rate sold 2 tickets of 5000 yen to one fan and one of them was resold
- **THEN** the Held Settlements of the two Orders together pay the Organizer 9500 yen

### Requirement: Nobody gets a seat twice and nobody is charged for nothing

A listing SHALL be sold to at most one fan. A fan whose resale checkout does not complete SHALL NOT be charged, and the listing SHALL be free again within 1 minute after their hold expires. A listing withdrawn before another fan holds it SHALL NOT be sold.

#### Scenario: Two fans, one listing
- **WHEN** one listing is free and two fans start a resale checkout for 1 ticket at the same moment
- **THEN** one fan holds it and buys it, and the other is told it is sold out for now and is not charged

#### Scenario: Purchase abandoned
- **WHEN** a fan holds the only listing at 12:00 and leaves
- **THEN** by 12:16 the listing is free again and the event page offers it

#### Scenario: Withdrawn first
- **WHEN** the listing fan withdraws before anyone starts buying
- **THEN** the event page offers no resale ticket and the fan's Ticket is 未入場

### Requirement: Resale closes when admission opens

No ticket SHALL be listed or bought through official resale once the event's admission window has opened, and a listing that has not sold by then SHALL leave its Ticket valid for entry.

#### Scenario: Unsold at the deadline
- **WHEN** a fan's listing has not sold when the admission window opens
- **THEN** the event page offers no resale and the fan's Ticket is admitted at the venue
