## MODIFIED Requirements

### Requirement: Persist Venues

The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support.

#### Scenario: Persist New Concerts

- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Persist Venues

- **WHEN** a discovered concert has a venue that does not exist in the database
- **THEN** a new venue is created dynamically based on the listed venue name provided by the source
- **AND** the new venue SHALL have `enrichment_status` set to `'pending'`
- **AND** the new concert is associated with this new venue

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation
