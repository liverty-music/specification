# TicketJourney.ListByUser

## Purpose

Returns every ticket journey of one fan, each naming its event and its status.

## Requirements

### Requirement: ListByUser returns all of the fan's journeys

ListByUser SHALL return every journey of the given fan, each with its event and its status, in no particular order and without pagination. It SHALL return an empty list when the fan has no journeys, and SHALL never include another fan's journey.

#### Scenario: The fan has journeys

- **WHEN** the fan has journeys for three events
- **THEN** ListByUser returns those three journeys, each with its event and status

#### Scenario: The fan has no journeys

- **WHEN** the fan has no journeys
- **THEN** ListByUser returns an empty list

#### Scenario: Other fans' journeys are excluded

- **WHEN** another fan has journeys for the same events
- **THEN** ListByUser for this fan returns only this fan's journeys
