# components/entity/ticket-journey/upsert-if-replaceable Specification

## Purpose
Stores a status that the platform or the app sets for a fan's journey only when the journey the fan has may be replaced by it: an inferred status never replaces a journey, and the platform's Applied never replaces a journey at Unpaid or Paid.

## Requirements

### Requirement: UpsertIfReplaceable stores the status only over a replaceable journey

UpsertIfReplaceable SHALL take a fan, an event, a status and who sets it (platform or inference), and SHALL store that status and its set by for the fan's journey for the event when the fan has no journey for it or when the fan's journey is replaceable by it (components/entity/ticket-journey, "Which journeys the platform and the app may replace"). Otherwise, and also when the journey already has the given status and status set by, it SHALL leave the journey unchanged. It SHALL report whether it stored the status. Checking and storing SHALL be one indivisible step with every other write of the same journey, so a status the fan stores at the same moment is never replaced. It SHALL fail with FailedPrecondition, storing nothing, when the event or the fan does not exist.

#### Scenario: No journey yet

- **WHEN** the fan has no journey for the event and UpsertIfReplaceable is called with Tracking set by inference
- **THEN** the fan's journey for the event is Tracking set by inference and the call reports that it stored the status

#### Scenario: Journey not replaceable

- **WHEN** the fan's journey for the event is Applied set by the fan and UpsertIfReplaceable is called with Tracking set by inference
- **THEN** the journey stays Applied set by the fan and the call reports that it stored nothing

#### Scenario: Same status again

- **WHEN** the fan's journey for the event is Applied set by the platform and UpsertIfReplaceable is called with Applied set by the platform
- **THEN** the journey is unchanged and the call reports that it stored nothing

#### Scenario: Entry over Tracking

- **WHEN** the fan's journey for the event is Tracking set by inference and UpsertIfReplaceable is called with Applied set by the platform
- **THEN** the journey is Applied set by the platform

#### Scenario: Fan writes at the same moment

- **WHEN** UpsertIfReplaceable is called with Applied set by the platform while the fan stores Paid for the same journey
- **THEN** the journey ends at Paid set by the fan

#### Scenario: Unknown event

- **WHEN** UpsertIfReplaceable is called for an event that does not exist
- **THEN** it fails with FailedPrecondition and no journey is stored

### Requirement: A stored status is announced with the change

When UpsertIfReplaceable stores a status, it SHALL announce the journey's status as changed (TicketJourney.StatusChanged), carrying the journey with its status and status set by, together with the change: both are stored or neither is. When it stores nothing or fails, it SHALL announce nothing. When the announcement cannot be recorded, it SHALL fail with Unavailable and leave the journey as it was.

#### Scenario: Status stored

- **WHEN** UpsertIfReplaceable stores Tracking set by inference
- **THEN** one status change is announced, carrying the journey at Tracking set by inference

#### Scenario: Nothing stored

- **WHEN** the fan's journey is not replaceable, or already has the given status and status set by, and UpsertIfReplaceable is called
- **THEN** nothing is announced
