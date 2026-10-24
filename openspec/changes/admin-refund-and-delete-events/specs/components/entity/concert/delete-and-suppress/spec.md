## MODIFIED Requirements

### Requirement: Delete and suppress together

DeleteAndSuppress SHALL remove the Event and, with it:
- its performers, its Concert and its TicketJourneys;
- the TicketTypes offered for it, with their lottery entries and Checkouts;
- the Refunded Orders of those lottery entries and Checkouts, with their Tickets and the Tickets' ResaleListings;
- the Reversed Settlements of those Orders;
- the Scanners of the Event, with their Admissions and RejectedScans;
- every Organizer's TicketSale the removal leaves without a TicketType;
- the Event's first-party Series when the removal leaves it with no Event.

It SHALL record a SuppressedConcert for the removed Event's Venue, date and start time. All of these effects SHALL happen together or not at all. A discovered Series and the Series' discovered TicketSales SHALL remain.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed and its slot is suppressed

#### Scenario: Series stays
- **WHEN** one Event of a Series with discovered TicketSales is deleted
- **THEN** the Series and its TicketSales remain

#### Scenario: Concert with an abandoned checkout
- **WHEN** a Concert whose TicketType has only an Expired Checkout whose card authorization was released is deleted
- **THEN** the Event, its TicketType and the Checkout are removed and its slot is suppressed

#### Scenario: Cancelled concert with refunded purchases
- **WHEN** a CANCELLED Event has only Refunded Orders, their Voided Tickets, one Sold ResaleListing, Reversed Settlements and a Scanner with Admissions
- **THEN** the Event and every one of those records are removed and its slot is suppressed

#### Scenario: Last event of a first-party series
- **WHEN** the only Event of a first-party Series is deleted
- **THEN** the Series is removed with it

#### Scenario: Other events of a first-party series
- **WHEN** one of two Events of a first-party Series is deleted
- **THEN** the Series and its other Event remain

### Requirement: Paid records block the delete

DeleteAndSuppress SHALL fail with FailedPrecondition, removing nothing and suppressing nothing, when the Event has:
- an Order that is not Refunded;
- a Settlement that is not Reversed;
- a purchase in progress: a Checkout that is Held or Committed, an Expired or Released Checkout whose card authorization is not yet released, or an Entered lottery entry.

#### Scenario: Concert with issued tickets
- **WHEN** an Event with an issued Ticket of a Paid Order is deleted
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a held settlement
- **WHEN** an Event whose Orders are Refunded has a Held Settlement
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a checkout in progress
- **WHEN** an Event has a Held Checkout
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with an open lottery entry
- **WHEN** an Event has an Entered lottery entry
- **THEN** the call fails with FailedPrecondition and the Event remains
