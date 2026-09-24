# List By User

## Purpose

Returns every ticket journey of a fan, as event and status pairs, so the fan's screens can show each event's status next to its concert.

## Requirements

### Requirement: ListByUser returns the fan's journeys

ListByUser SHALL return the fan's journeys as TicketJourney.ListByUser returns them. When that read fails, ListByUser SHALL fail with that error.

#### Scenario: The fan has journeys

- **WHEN** the fan has journeys for two events
- **THEN** ListByUser returns both journeys with their events and statuses

#### Scenario: The fan has no journeys

- **WHEN** the fan has no journeys
- **THEN** ListByUser returns an empty list

#### Scenario: Reading fails

- **WHEN** TicketJourney.ListByUser fails
- **THEN** ListByUser fails with that error
