## ADDED Requirements

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
