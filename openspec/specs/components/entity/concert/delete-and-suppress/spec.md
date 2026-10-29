# Concert.DeleteAndSuppress

## Purpose

Removes a Concert from the catalog together with what depends only on it, and records its slot as a SuppressedConcert.

## Requirements

### Requirement: Delete is idempotent

DeleteAndSuppress on an id that does not exist SHALL succeed and SHALL record no SuppressedConcert; suppressing a slot that is already suppressed SHALL succeed without a second record.

#### Scenario: Unknown id
- **WHEN** the Event id does not exist
- **THEN** the call succeeds and no SuppressedConcert is recorded

#### Scenario: Slot already suppressed
- **WHEN** an Event at an already-suppressed slot is deleted
- **THEN** the call succeeds and the slot has one SuppressedConcert

### Requirement: Paid records and purchases in progress block the delete

DeleteAndSuppress SHALL fail with FailedPrecondition, removing nothing and suppressing nothing, when the Event has:
- an Order that is Paid;
- a Settlement that is not Reversed;
- a purchase in progress: a Pending Order, or a Void Order whose card authorization is not yet released.

A purchase started while DeleteAndSuppress runs SHALL either be seen by this check or be refused; it SHALL NOT be removed.

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

### Requirement: Delete and suppress an event with its records

DeleteAndSuppress SHALL remove the Event and, with it:
- its performers, its Concert and its TicketJourneys;
- its TicketStocks, with their Orders that are Void or Refunded and the lottery entries and Checkouts of those Orders;
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
