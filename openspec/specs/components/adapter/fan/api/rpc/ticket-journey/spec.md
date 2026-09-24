# Ticket Journey RPC

## Purpose

The fan-facing ticket journey service boundary: it resolves the signed-in fan for every call and rejects malformed requests before any usecase runs.

## Requirements

### Requirement: Every call acts for the signed-in fan

SetStatus, Delete and ListByUser SHALL act only on the journeys of the signed-in fan who makes the call; a request cannot name another fan. Each call SHALL fail with Unauthenticated when the caller is not signed in, and with NotFound when the signed-in caller has no account, before any journey is read or changed.

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls SetStatus, Delete or ListByUser
- **THEN** the call fails with Unauthenticated and no journey is read or changed

#### Scenario: Caller has no account

- **WHEN** a signed-in caller who has no account calls SetStatus
- **THEN** the call fails with NotFound and no journey is changed

#### Scenario: The journey belongs to the caller

- **WHEN** a signed-in fan sets Tracking for an event
- **THEN** the journey recorded is the caller's own journey for that event

### Requirement: SetStatus request validation

SetStatus SHALL fail with InvalidArgument, before TicketJourneyUseCase.SetStatus runs, when the event id is missing or not a well-formed event id, or when the status is missing or is not one of the five journey statuses. A well-formed event id for an event that does not exist fails with FailedPrecondition, as TicketJourney.Upsert returns it.

#### Scenario: Missing or malformed event id

- **WHEN** SetStatus is called without an event id, or with one that is not well formed
- **THEN** it fails with InvalidArgument and nothing is recorded

#### Scenario: Missing or unknown status

- **WHEN** SetStatus is called without a status, or with a value that is not one of the five journey statuses
- **THEN** it fails with InvalidArgument and nothing is recorded

#### Scenario: Event does not exist

- **WHEN** SetStatus is called with a well-formed event id of an event that does not exist
- **THEN** it fails with FailedPrecondition

### Requirement: Delete request validation

Delete SHALL fail with InvalidArgument, before TicketJourneyUseCase.Delete runs, when the event id is missing or not a well-formed event id.

#### Scenario: Missing or malformed event id

- **WHEN** Delete is called without an event id, or with one that is not well formed
- **THEN** it fails with InvalidArgument and nothing is removed

### Requirement: ListByUser response

ListByUser SHALL return each of the caller's journeys with its event, its status and the caller as its owner, and SHALL return an empty list, not an error, when the caller has no journeys.

#### Scenario: The caller has no journeys

- **WHEN** a signed-in fan with no journeys calls ListByUser
- **THEN** the call succeeds with an empty list
