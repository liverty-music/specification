# Spec Delta

## MODIFIED Requirements

### Requirement: Delete and suppress an event with its records

DeleteAndSuppress SHALL remove the Event and, with it:
- its performers, its Concert and its TicketJourneys;
- its TicketStocks, with their Orders that are Void or Refunded and the lottery entries, Checkouts, resale entries and CardAuthorizations of those Orders;
- the Tickets of those Orders and the Tickets' ResaleListings;
- the Reversed Settlements of those Orders;
- the Scanners of the Event, with their Admissions and RejectedScans;
- every Organizer's TicketSale the removal leaves naming no event;
- the Event's first-party Series, with its SeatTypes, when the removal leaves it with no Event.

It SHALL record a SuppressedConcert for the removed Event's Venue, date and start time. All of these effects SHALL happen together or not at all. A discovered Series and the Series' discovered TicketSales SHALL remain.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed and its slot is suppressed

#### Scenario: Series stays
- **WHEN** one Event of a Series with discovered TicketSales is deleted
- **THEN** the Series and its TicketSales remain

#### Scenario: Concert with an abandoned checkout
- **WHEN** a Concert whose TicketStock has only a Void Order of an Expired Checkout whose card authorization was released is deleted
- **THEN** the Event, its TicketStock, the Order and the Checkout are removed and its slot is suppressed

#### Scenario: Cancelled concert with refunded purchases
- **WHEN** a CANCELLED Event has only Refunded Orders, their Voided Tickets, one Sold ResaleListing, Reversed Settlements and a Scanner with Admissions
- **THEN** the Event and every one of those records are removed and its slot is suppressed

#### Scenario: Last event of a first-party series
- **WHEN** the only Event of a first-party Series is deleted
- **THEN** the Series and its SeatTypes are removed with it

#### Scenario: Other events of a first-party series
- **WHEN** one of two Events of a first-party Series is deleted
- **THEN** the Series, its SeatTypes and its other Event remain
