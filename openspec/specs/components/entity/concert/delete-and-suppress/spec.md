# Concert.DeleteAndSuppress

## Purpose

Removes a Concert from the catalog together with what depends only on it, and records its slot as a SuppressedConcert.

## Requirements

### Requirement: Delete and suppress together

DeleteAndSuppress SHALL remove the Event and, with it, its performers, its Concert, its TicketJourneys, and its lottery sales phases with their ticket applications, and SHALL record a SuppressedConcert for the removed Event's Venue, date and start time. Both effects SHALL happen together or not at all. The Event's Series and the Series' SalesPhases SHALL remain.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed and its slot is suppressed

#### Scenario: Series stays
- **WHEN** one Event of a Series with SalesPhases is deleted
- **THEN** the Series and its SalesPhases remain

### Requirement: Paid records block the delete

DeleteAndSuppress SHALL fail with FailedPrecondition, removing nothing and suppressing nothing, when the Event has a Ticket, an Order or a Settlement.

#### Scenario: Concert with issued tickets
- **WHEN** an Event with an issued Ticket is deleted
- **THEN** the call fails with FailedPrecondition and the Event remains

### Requirement: Delete is idempotent

DeleteAndSuppress on an id that does not exist SHALL succeed and SHALL record no SuppressedConcert; suppressing a slot that is already suppressed SHALL succeed without a second record.

#### Scenario: Unknown id
- **WHEN** the Event id does not exist
- **THEN** the call succeeds and no SuppressedConcert is recorded

#### Scenario: Slot already suppressed
- **WHEN** an Event at an already-suppressed slot is deleted
- **THEN** the call succeeds and the slot has one SuppressedConcert
