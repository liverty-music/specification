# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: ListByUser response`
- TO: `### Requirement: List response`

## MODIFIED Requirements

### Requirement: Every call acts for the signed-in fan

SetStatus, Delete and List SHALL act only on the journeys of the signed-in fan who makes the call; a request cannot name another fan. Each call SHALL fail with Unauthenticated when the caller is not signed in, and with NotFound when the signed-in caller has no account, before any journey is read or changed.

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls SetStatus, Delete or List
- **THEN** the call fails with Unauthenticated and no journey is read or changed

#### Scenario: Caller has no account

- **WHEN** a signed-in caller who has no account calls SetStatus
- **THEN** the call fails with NotFound and no journey is changed

#### Scenario: The journey belongs to the caller

- **WHEN** a signed-in fan sets Tracking for an event
- **THEN** the journey recorded is the caller's own journey for that event

### Requirement: List response

List SHALL return each of the caller's journeys with its event, its status and the caller as its owner, and SHALL return an empty list, not an error, when the caller has no journeys.

#### Scenario: The caller has no journeys

- **WHEN** a signed-in fan with no journeys calls List
- **THEN** the call succeeds with an empty list
