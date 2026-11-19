# components/entity/concert/delete Specification

## Purpose
Removes a Concert from the catalog together with every record that depends only on it, refused while one of its purchases is still live.

## Requirements

### Requirement: Delete is idempotent

Delete on an id that does not exist SHALL succeed and change nothing.

#### Scenario: Unknown id
- **WHEN** the Event id does not exist
- **THEN** the call succeeds and nothing changes

### Requirement: Paid records and purchases in progress block the delete

Delete SHALL fail with FailedPrecondition, removing nothing, when the Event has:
- an Order that is Paid;
- a Settlement that is not Reversed;
- a purchase in progress: a Pending Order.

A purchase started while Delete runs SHALL either be seen by this check or be refused; it SHALL NOT be removed.

#### Scenario: Concert with issued tickets
- **WHEN** an Event with an issued Ticket of a Paid Order is deleted
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a held settlement
- **WHEN** an Event whose Orders are Refunded has a Held Settlement
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a checkout in progress
- **WHEN** an Event has a Pending Order of a Held Checkout
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with an open lottery entry
- **WHEN** an Event has a Pending Order of an Entered lottery entry
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a won entry awaiting its order
- **WHEN** an Event has a Won lottery entry whose payment is captured and whose Order is still Pending
- **THEN** the call fails with FailedPrecondition and the Event and the entry remain

### Requirement: Delete an event with its records

Delete SHALL remove the Event and, with it:
- its performers, its Concert and its TicketJourneys;
- its TicketStocks, with the Orders that leave with their Event (see Order, "An Order leaves with its Event only when ended") and the lottery entries, Checkouts, resale entries and CardAuthorizations of those Orders;
- the Tickets of those Orders and the Tickets' ResaleListings;
- the Reversed Settlements of those Orders;
- the Scanners of the Event, with their Admissions and RejectedScans;
- every Organizer's TicketSale the removal leaves naming no event;
- the Event's Series when it leaves with its last Event (see Series, "A first-party series leaves with its last event"), with its SeatTypes.

All of these effects SHALL happen together or not at all. A discovered Series and the Series' discovered TicketSales SHALL remain. Delete SHALL record nothing about the removed Event's Venue, date or start time, so a Concert can be created at that slot again.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed

#### Scenario: Series stays
- **WHEN** one Event of a Series with discovered TicketSales is deleted
- **THEN** the Series and its TicketSales remain

#### Scenario: Concert with an abandoned checkout
- **WHEN** a Concert whose TicketStock has only a Void Order of an Expired Checkout whose card authorization was released is deleted
- **THEN** the Event, its TicketStock, the Order and the Checkout are removed

#### Scenario: Cancelled concert with refunded purchases
- **WHEN** a CANCELLED Event has only Refunded Orders, their Voided Tickets, one Sold ResaleListing, Reversed Settlements and a Scanner with Admissions
- **THEN** the Event and every one of those records are removed

#### Scenario: Last event of a first-party series
- **WHEN** the only Event of a first-party Series is deleted
- **THEN** the Series and its SeatTypes are removed with it

#### Scenario: Other events of a first-party series
- **WHEN** one of two Events of a first-party Series is deleted
- **THEN** the Series, its SeatTypes and its other Event remain

#### Scenario: Same slot created again after the delete
- **WHEN** an Event is deleted and a Concert at the same Venue, date and start time is then created (Concert.Create)
- **THEN** a new Event is created at that slot
