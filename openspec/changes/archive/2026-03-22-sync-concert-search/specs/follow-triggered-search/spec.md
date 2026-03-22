## MODIFIED Requirements

### Requirement: Trigger concert search on first follow
When a user follows an artist and no search log exists for that artist, the system SHALL launch a concert search via `SearchNewConcerts`. The search runs synchronously within the follow goroutine context.

#### Scenario: First follow triggers search
- **WHEN** a user follows an artist that has no entry in the search log
- **THEN** the system SHALL call `SearchNewConcerts(artistID)` in a background goroutine
- **AND** the search SHALL block until the Gemini API completes (synchronous)

#### Scenario: Subsequent follow skips search
- **WHEN** a user follows an artist that already has a search log entry
- **THEN** the system SHALL NOT trigger a search

#### Scenario: Already-following is treated as no-op
- **WHEN** a user follows an artist they already follow (ErrAlreadyExists)
- **THEN** the system SHALL return success without checking the search log or triggering search
