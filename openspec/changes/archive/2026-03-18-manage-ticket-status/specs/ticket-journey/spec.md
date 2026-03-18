## ADDED Requirements

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
- **AND** `LOST` SHALL represent both lottery failure (落選) and payment deadline expiration (入金期限切れ)

### Requirement: Set Ticket Journey Status

The system SHALL allow an authenticated user to set (create or update) their ticket journey status for a given event via a single upsert operation.

#### Scenario: Set status on a new journey

- **WHEN** an authenticated user calls `SetStatus` with an `event_id` and `status`
- **AND** no journey exists for that user and event
- **THEN** the system SHALL create a new `TicketJourney` with the given status
- **AND** the user_id SHALL be derived from the authentication context

#### Scenario: Update status on an existing journey

- **WHEN** an authenticated user calls `SetStatus` with an `event_id` and `status`
- **AND** a journey already exists for that user and event
- **THEN** the system SHALL update the existing journey's status

#### Scenario: Any status transition is allowed

- **WHEN** a user calls `SetStatus` with any valid status value
- **THEN** the system SHALL accept the transition regardless of the current status
- **AND** the system SHALL NOT enforce a state machine or transition rules

#### Scenario: Invalid status value rejected

- **WHEN** a user calls `SetStatus` with `UNSPECIFIED` or an undefined enum value
- **THEN** the system SHALL return an `INVALID_ARGUMENT` error

#### Scenario: Invalid event_id rejected

- **WHEN** a user calls `SetStatus` with a malformed or missing `event_id`
- **THEN** the system SHALL return an `INVALID_ARGUMENT` error

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

### Requirement: Ticket Journey Database Schema

The system SHALL store ticket journeys in a `ticket_journeys` table with a composite primary key.

#### Scenario: Table structure

- **WHEN** the `ticket_journeys` table is created
- **THEN** it SHALL have columns: `user_id` (UUID, FK → users), `event_id` (UUID, FK → events), `status` (SMALLINT)
- **AND** the primary key SHALL be `(user_id, event_id)`
- **AND** it SHALL NOT include `created_at` or `updated_at` columns

#### Scenario: Upsert operation

- **WHEN** a `SetStatus` operation targets an existing `(user_id, event_id)` pair
- **THEN** the database SHALL perform `INSERT ... ON CONFLICT (user_id, event_id) DO UPDATE SET status`
