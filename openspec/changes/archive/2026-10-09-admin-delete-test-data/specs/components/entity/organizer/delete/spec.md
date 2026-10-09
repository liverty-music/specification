# Spec Delta

## Purpose

Organizer.Delete permanently removes an Organizer's records: the Organizer with its Series, Events, purchases for those Events, Media records and associations. Nothing that blocks deletion may be removed.

## ADDED Requirements

### Requirement: Delete removes the Organizer and everything recorded for it

Delete SHALL remove, together or not at all:

- the Organizer;
- its first-party Series and their Events, with each Event's lottery sales phases, ticket applications, ticket journeys and performers;
- the Orders and Tickets for those Events, with their Reversed Settlements;
- the reception links of those Events, with their admissions and rejected scans;
- its Media records and the Series' cover links;
- its Artist associations and its payout-account record.

Fans' follows of the Artists, and every record unrelated to the Organizer, SHALL remain.

#### Scenario: Organizer with a published Series

- **WHEN** Delete runs for a deactivated Organizer with one Series, one Event, a cover Media and one associated Artist
- **THEN** none of the Organizer, Series, Event, Media record or association exists afterwards, and the Artist and its followers remain

#### Scenario: Refunded purchase

- **WHEN** an Event of the Organizer has one Order that is Refunded and the Ticket issued for it
- **THEN** the Order, the Ticket and the Order's Reversed Settlement are removed with the Event

### Requirement: Delete refuses when deletion is blocked

Delete SHALL fail with FailedPrecondition and remove nothing when, at the moment it runs:

- the Organizer is not deactivated;
- any of its Events has an Order that is not Refunded;
- any of its Events has a Settlement that is not Reversed;
- the Organizer has a payout-account record.

#### Scenario: Active Organizer

- **WHEN** Delete runs for an active Organizer
- **THEN** it fails with FailedPrecondition and the Organizer and its Series remain

#### Scenario: Paid order

- **WHEN** an Event of the Organizer has a Paid Order
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Settlement

- **WHEN** an Event of the Organizer has a Held or Released Settlement
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Payout account

- **WHEN** the Organizer has a payout-account record
- **THEN** it fails with FailedPrecondition and nothing is removed

### Requirement: Unknown Organizer

Delete SHALL fail with NotFound when no Organizer has the id.

#### Scenario: Unknown id

- **WHEN** no Organizer has the id
- **THEN** Delete fails with NotFound
