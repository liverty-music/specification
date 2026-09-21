# Ticket Journey

## Purpose

The `ticket-journey` capability allows users to track their personal ticket acquisition status for concerts and events. Users can set, update, and remove journey statuses representing stages of the ticket acquisition process (tracking, applied, lost, unpaid, paid).

## Requirements

### Requirement: Ticket Journey Entity

The system SHALL define a `TicketJourney` entity representing a user's personal ticket acquisition status for a specific event. Each journey is uniquely identified by the combination of user and event.

#### Scenario: TicketJourney data model

- **WHEN** a ticket journey is represented
- **THEN** it SHALL include a `user_id` (UserId), `event_id` (EventId), and `status` (TicketJourneyStatus)
- **AND** the composite key SHALL be `(user_id, event_id)` — one journey per user per event

#### Scenario: TicketJourneyStatus enum values

- **WHEN** a ticket journey status is represented
- **THEN** it SHALL be one of: `TRACKING`, `APPLIED`, `LOST`, `UNPAID`, `PAID`
- **AND** `UNSPECIFIED` (value 0) SHALL exist as the default proto value but SHALL NOT be accepted in API requests
- **AND** `LOST` SHALL represent both lottery failure and payment deadline expiration
