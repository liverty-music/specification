# List

## Purpose

Returns every ticket journey of a fan, as event and status pairs, so the fan's screens can show each event's status next to its concert.

## Requirements

### Requirement: List returns the fan's journeys

List SHALL return the fan's journeys as TicketJourney.ListByUser returns them. When that read fails, List SHALL fail with that error.

#### Scenario: The fan has journeys

- **WHEN** the fan has journeys for two events
- **THEN** List returns both journeys with their events and statuses

#### Scenario: The fan has no journeys

- **WHEN** the fan has no journeys
- **THEN** List returns an empty list

#### Scenario: Reading fails

- **WHEN** TicketJourney.ListByUser fails
- **THEN** List fails with that error
