# Spec Delta

## ADDED Requirements

### Requirement: A ticket of a sold-out seat type is listed

After a TicketStock sold out, a signed-in fan holding Issued Tickets of it, bought first come or won in a lottery, SHALL be able to list one with ResaleListingUseCase.Create and see it Listed with ResaleListingUseCase.List; the Ticket stays valid for entry while it is listed and not sold. Buying a listed ticket arrives with the change resell-tickets-by-lottery.

#### Scenario: One of two tickets listed
- **WHEN** a fan holding 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one
- **THEN** ResaleListingUseCase.List shows the listing Listed at 5000 yen and both of the fan's Tickets stay 未入場 and valid for entry

#### Scenario: Lottery-won ticket listed
- **WHEN** a fan who won 2 S席 tickets in the event's lottery presale lists one after S席 sold out
- **THEN** the listing is Listed

## REMOVED Requirements

### Requirement: A ticket is resold and its fan refunded

**Reason**: Buying a listed ticket no longer goes through the first-come checkout; official resale purchases become a lottery in the change resell-tickets-by-lottery, which restates the purchase, the refund and the sold email.
**Migration**: See "A ticket of a sold-out seat type is listed" for the listing part; the purchase part returns with resell-tickets-by-lottery.

### Requirement: The Organizer is paid once per seat

**Reason**: It describes the outcome of a resale purchase, which moves to the change resell-tickets-by-lottery.
**Migration**: Restated by resell-tickets-by-lottery.

### Requirement: Nobody gets a seat twice and nobody is charged for nothing

**Reason**: It describes resale checkouts, which no longer exist; the resale lottery of resell-tickets-by-lottery states its own guarantees.
**Migration**: Restated by resell-tickets-by-lottery.
