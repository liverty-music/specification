## MODIFIED Requirements

### Requirement: Delete removes the Organizer and everything recorded for it

Delete SHALL remove, together or not at all:

- the Organizer;
- its first-party Series with their TicketSales, and their Events, with each Event's TicketTypes, lottery entries, Checkouts, ticket journeys and performers;
- the Refunded and Failed Orders and their Tickets for those Events, with their Reversed Settlements and the Tickets' ResaleListings;
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

### Requirement: Delete refuses when deletion is blocked

Delete SHALL fail with FailedPrecondition and remove nothing when, at the moment it runs:

- the Organizer is not deactivated;
- any of its Events has an Order that is Paid;
- any of its Events has a Settlement that is not Reversed;
- any of its Events has a purchase in progress: a Checkout that is Held or Committed, an Expired or Released Checkout whose card authorization is not yet released, an Entered lottery entry, a Draft lottery entry whose card authorization is open, or a Won lottery entry whose Order is not yet issued;
- the Organizer has a payout-account record.

A purchase started while Delete runs SHALL either be seen by these checks or be refused; it SHALL NOT be removed.

#### Scenario: Active Organizer

- **WHEN** Delete runs for an active Organizer
- **THEN** it fails with FailedPrecondition and the Organizer and its Series remain

#### Scenario: Paid order

- **WHEN** an Event of the Organizer has a Paid Order
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Settlement

- **WHEN** an Event of the Organizer has a Held or Released Settlement
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Purchase in progress

- **WHEN** an Event of the Organizer has an Entered lottery entry
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Draft entry with a card authorization

- **WHEN** an Event of the Organizer has a Draft lottery entry whose card authorization is open
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Won entry awaiting its order

- **WHEN** an Event of the Organizer has a Won lottery entry whose Order is not yet issued
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Payout account

- **WHEN** the Organizer has a payout-account record
- **THEN** it fails with FailedPrecondition and nothing is removed
