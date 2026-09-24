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
