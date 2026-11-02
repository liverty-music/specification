# TicketJourney.Upsert

## Purpose

Records a fan's status for one event: it creates the fan's journey for the event, or replaces the status of the journey that already exists.

## Requirements

### Requirement: Upsert creates or replaces the fan's journey

Upsert SHALL leave exactly one journey for the given fan and event, carrying the given status. When no journey exists it SHALL create one; when one exists it SHALL replace its status. Upserting the status a journey already has SHALL succeed and leave the journey unchanged. Upsert SHALL NOT change any other fan's journey or any other event's journey.

#### Scenario: First status for an event

- **WHEN** the fan has no journey for the event and Upsert is called with Tracking
- **THEN** the fan has one journey for the event with status Tracking

#### Scenario: Replacing the status

- **WHEN** the fan's journey for the event is Applied and Upsert is called with Lost
- **THEN** the fan still has one journey for the event, now with status Lost

#### Scenario: Same status again

- **WHEN** the fan's journey for the event is Paid and Upsert is called with Paid
- **THEN** Upsert succeeds and the journey is still Paid

### Requirement: Upsert requires an existing fan and event

Upsert SHALL fail with FailedPrecondition, and store nothing, when the event or the fan does not exist.

#### Scenario: Unknown event

- **WHEN** Upsert is called for an event that does not exist
- **THEN** it fails with FailedPrecondition and no journey is stored

### Requirement: A changed status is announced with the change

When Upsert creates a journey or changes its status, it SHALL announce the journey's status change, carrying the journey with its new status, together with the change: both are stored or neither is. When the journey already has the given status, Upsert SHALL announce nothing. When the announcement cannot be recorded, Upsert SHALL fail with Unavailable and the journey SHALL stay as it was, or stay absent.

#### Scenario: First status announced

- **WHEN** the fan has no journey for the event and Upsert is called with Tracking
- **THEN** one status change is announced, carrying the journey at Tracking

#### Scenario: Status changed

- **WHEN** the fan's journey for the event is Applied and Upsert is called with Lost
- **THEN** one status change is announced, carrying the journey at Lost

#### Scenario: Same status again

- **WHEN** the fan's journey for the event is Paid and Upsert is called with Paid
- **THEN** Upsert succeeds and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the fan's journey is Applied, Upsert is called with Lost and the announcement cannot be recorded
- **THEN** Upsert fails with Unavailable and the journey stays Applied
