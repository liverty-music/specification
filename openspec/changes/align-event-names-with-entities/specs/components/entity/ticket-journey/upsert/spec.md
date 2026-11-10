## MODIFIED Requirements

### Requirement: A changed status is announced with the change

When Upsert creates a journey or changes its status or status set by, it SHALL announce the journey's status as changed (TicketJourney.StatusChanged), carrying the journey with its new status and status set by, together with the change: both are stored or neither is. When the journey already has the given status and status set by, Upsert SHALL announce nothing. When the announcement cannot be recorded, Upsert SHALL fail with Unavailable and the journey SHALL stay as it was, or stay absent.

#### Scenario: First status announced

- **WHEN** the fan has no journey for the event and Upsert is called with Tracking set by the fan
- **THEN** one status change is announced, carrying the journey at Tracking set by the fan

#### Scenario: Status changed

- **WHEN** the fan's journey for the event is Applied and Upsert is called with Lost set by the fan
- **THEN** one status change is announced, carrying the journey at Lost set by the fan

#### Scenario: The fan confirms an inferred status

- **WHEN** the fan's journey for the event is Tracking set by inference and Upsert is called with Tracking set by the fan
- **THEN** one status change is announced, carrying the journey at Tracking set by the fan

#### Scenario: Same status again

- **WHEN** the fan's journey for the event is Paid set by the platform and Upsert is called with Paid set by the platform
- **THEN** Upsert succeeds and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the fan's journey is Applied, Upsert is called with Lost and the announcement cannot be recorded
- **THEN** Upsert fails with Unavailable and the journey stays Applied
