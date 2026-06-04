## MODIFIED Requirements

### Requirement: Set Ticket Journey Status

The system SHALL allow an authenticated user to set (create or update) their ticket journey status for a given event via a single upsert operation. Status can be set manually by the user or as a side effect of confirming a ticket email import.

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

#### Scenario: Status set via ticket email confirmation

- **WHEN** a user confirms a ticket email import via `UpdateTicketEmail`
- **THEN** the system SHALL set the `TicketJourney` status for each associated event based on the parsed email content
- **AND** for `LOTTERY_INFO` emails, the status SHALL be set to `TRACKING`
- **AND** for `LOTTERY_RESULT` emails with a win and pending payment, the status SHALL be set to `UNPAID`
- **AND** for `LOTTERY_RESULT` emails with a win and completed payment, the status SHALL be set to `PAID`
- **AND** for `LOTTERY_RESULT` emails with a loss, the status SHALL be set to `LOST`
