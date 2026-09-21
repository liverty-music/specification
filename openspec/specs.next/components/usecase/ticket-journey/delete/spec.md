# Delete

## Purpose

The `ticket-journey` capability allows users to track their personal ticket acquisition status for concerts and events. Users can set, update, and remove journey statuses representing stages of the ticket acquisition process (tracking, applied, lost, unpaid, paid).

## Requirements

### Requirement: Delete Ticket Journey

The system SHALL allow an authenticated user to remove their ticket journey for a given event.

#### Scenario: Delete an existing journey

- **WHEN** an authenticated user calls `Delete` with an `event_id`
- **AND** a journey exists for that user and event
- **THEN** the system SHALL remove the journey record

#### Scenario: Delete a non-existent journey

- **WHEN** an authenticated user calls `Delete` with an `event_id`
- **AND** no journey exists for that user and event
- **THEN** the system SHALL return successfully (idempotent delete)
