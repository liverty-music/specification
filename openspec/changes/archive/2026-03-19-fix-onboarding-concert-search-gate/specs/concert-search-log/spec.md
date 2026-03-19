## ADDED Requirements

### Requirement: Frontend search status polling for onboarding

The frontend SHALL poll the `ListSearchStatuses` RPC during onboarding to detect when backend concert searches have actually completed, rather than relying on the `SearchNewConcerts` RPC return (which is fire-and-forget).

#### Scenario: Polling starts after SearchNewConcerts fires

- **WHEN** the frontend calls `SearchNewConcerts` for an artist during onboarding
- **THEN** the system SHALL add the artist ID to the set of pending searches
- **AND** the system SHALL start (or continue) a polling timer if not already running

#### Scenario: Batched polling every 2 seconds

- **WHEN** the polling timer fires
- **AND** there are one or more artist IDs with pending search status
- **THEN** the system SHALL call `ListSearchStatuses` with all pending artist IDs in a single batched request
- **AND** for each artist whose status is `COMPLETED` or `FAILED`, the system SHALL mark that artist's search as done
- **AND** for each artist whose status is `PENDING` or `UNSPECIFIED`, the system SHALL keep it in the pending set for the next poll cycle

#### Scenario: Polling stops when all searches resolve

- **WHEN** all artist IDs in the pending set have reached a terminal state (`COMPLETED`, `FAILED`, or timed out)
- **THEN** the system SHALL clear the polling interval timer
- **AND** the system SHALL trigger concert data verification (`verifyConcertData`)

#### Scenario: Per-artist timeout as polling deadline

- **WHEN** an artist's search has been pending for 15 seconds (measured from the time `SearchNewConcerts` was fired)
- **AND** the artist's status has not yet reached `COMPLETED` or `FAILED`
- **THEN** the system SHALL treat the artist's search as done (timed out)
- **AND** the system SHALL remove the artist from the pending set

#### Scenario: Polling error handling

- **WHEN** a `ListSearchStatuses` poll call fails with a network or RPC error
- **THEN** the system SHALL log the error
- **AND** the system SHALL NOT mark any artists as done
- **AND** the system SHALL retry on the next poll cycle (2 seconds later)
- **AND** the per-artist 15-second timeout SHALL still apply independently of poll errors
