# List By User

## Purpose

The `ticket-journey` capability allows users to track their personal ticket acquisition status for concerts and events. Users can set, update, and remove journey statuses representing stages of the ticket acquisition process (tracking, applied, lost, unpaid, paid).

## Requirements

### Requirement: List Ticket Journeys by User

The system SHALL allow an authenticated user to retrieve all their ticket journeys.

#### Scenario: User has journeys

- **WHEN** an authenticated user calls `ListByUser`
- **THEN** the system SHALL return all `TicketJourney` records for that user
- **AND** each record SHALL contain `event_id` and `status`

#### Scenario: User has no journeys

- **WHEN** an authenticated user calls `ListByUser`
- **AND** the user has no ticket journeys
- **THEN** the system SHALL return an empty list
