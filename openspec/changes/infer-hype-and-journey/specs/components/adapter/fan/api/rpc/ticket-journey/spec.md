## MODIFIED Requirements

### Requirement: Every call acts for the signed-in fan

SetStatus, InferTracking, Delete and List SHALL act only on the journeys of the signed-in fan who makes the call; a request cannot name another fan. Each call SHALL fail with Unauthenticated when the caller is not signed in, and with NotFound when the signed-in caller has no account, before any journey is read or changed.

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls SetStatus, InferTracking, Delete or List
- **THEN** the call fails with Unauthenticated and no journey is read or changed

#### Scenario: Caller has no account

- **WHEN** a signed-in caller who has no account calls SetStatus
- **THEN** the call fails with NotFound and no journey is changed

#### Scenario: The journey belongs to the caller

- **WHEN** a signed-in fan sets Tracking for an event
- **THEN** the journey recorded is the caller's own journey for that event

## ADDED Requirements

### Requirement: InferTracking request validation and response

InferTracking SHALL fail with InvalidArgument, before TicketJourneyUseCase.InferTracking runs, when the event id is missing or not a well-formed event id. A well-formed event id for an event that does not exist fails with FailedPrecondition. The response SHALL say whether tracking started.

#### Scenario: Missing event id

- **WHEN** InferTracking is called without an event id
- **THEN** it fails with InvalidArgument and nothing is recorded

#### Scenario: Tracking started

- **WHEN** a signed-in fan with no journey for the event calls InferTracking
- **THEN** the response says tracking started
