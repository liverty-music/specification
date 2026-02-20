## MODIFIED Requirements

### Requirement: Concert Persistence
The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support. The bulk insert SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Persist New Concerts
- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Bulk insert uses unnest
- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction
- **AND** no `maxConcertsPerBatch` batching loop SHALL be required

#### Scenario: Single concert creation
- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation
