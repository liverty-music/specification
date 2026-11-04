# Spec Delta

## MODIFIED Requirements

### Requirement: Delete removes the Organizer and everything recorded for it

Delete SHALL remove, together or not at all:

- the Organizer;
- its first-party Series with their SeatTypes and TicketSales, and their Events, with each Event's TicketStocks, ticket journeys and performers;
- the Void and Refunded Orders for those Events with their lottery entries, Checkouts, resale entries, CardAuthorizations and Tickets, the Orders' Reversed Settlements and the Tickets' ResaleListings;
- the Scanners of those Events, with their Admissions and RejectedScans;
- its SeriesImage records and the Series' cover links;
- its Artist associations and its payout-account record.

Fans' follows of the Artists, and every record unrelated to the Organizer, SHALL remain.

#### Scenario: Organizer with a published Series

- **WHEN** Delete runs for a deactivated Organizer with one Series, one Event, a cover SeriesImage and one associated Artist
- **THEN** none of the Organizer, Series, Event, SeriesImage record or association exists afterwards, and the Artist and its followers remain

#### Scenario: Refunded purchase

- **WHEN** an Event of the Organizer has one Order that is Refunded and the Ticket issued for it
- **THEN** the Order, the Ticket and the Order's Reversed Settlement are removed with the Event

#### Scenario: Resold ticket

- **WHEN** a Ticket of an Event of the Organizer was resold, so the Event has a Sold ResaleListing, and every Order of the Event is Refunded
- **THEN** the ResaleListing is removed with the Event and the Organizer is deleted

#### Scenario: Abandoned application

- **WHEN** an Event of the Organizer has only a Void Order of a Lost lottery entry whose card authorization was released
- **THEN** the Order and the entry are removed with the Event
