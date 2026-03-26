## MODIFIED Requirements

### Requirement: Trigger concert search on first follow
When a user follows an artist and no search log exists for that artist, the system SHALL launch a background concert search via `SearchNewConcerts`. The frontend SHALL NOT independently call `SearchNewConcerts` after a follow — concert discovery is solely the responsibility of the backend (first-follow trigger) and the daily cronjob.

#### Scenario: First follow triggers search
- **WHEN** a user follows an artist that has no entry in the search log
- **THEN** the system SHALL asynchronously call `SearchNewConcerts(artistID)` in a background goroutine

#### Scenario: Subsequent follow skips search
- **WHEN** a user follows an artist that already has a search log entry
- **THEN** the system SHALL NOT trigger a background search

#### Scenario: Already-following is treated as no-op
- **WHEN** a user follows an artist they already follow (ErrAlreadyExists)
- **THEN** the system SHALL return success without checking the search log or triggering search

#### Scenario: Frontend does not call SearchNewConcerts after follow
- **WHEN** a user follows an artist from the Discovery page
- **THEN** the frontend SHALL NOT call the `SearchNewConcerts` RPC
- **AND** the backend MUST be the sole initiator of concert discovery

### Requirement: Search errors do not affect follow operation
The Follow RPC response SHALL NOT be affected by background search success or failure.

#### Scenario: Search fails silently
- **WHEN** a background search triggered by follow encounters an error
- **THEN** the system SHALL log the error and NOT propagate it to the Follow caller

### Requirement: Search log check failure is non-blocking
The system SHALL treat search log lookup errors (other than NotFound) as non-fatal during follow.

#### Scenario: Search log lookup fails
- **WHEN** `searchLogRepo.GetByArtistID` returns an unexpected error
- **THEN** the system SHALL log the error and skip the background search (do not trigger search on ambiguous state)
