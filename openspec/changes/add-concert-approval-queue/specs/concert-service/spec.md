## MODIFIED Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. Error returns SHALL include contextual wrapping indicating which operation failed.

#### Scenario: Successful Search with known official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has a persisted official site record
- **THEN** the system returns a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database
- **AND** results exclude concerts that are already present in the approval queue in `pending` state

#### Scenario: Successful Search without official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has no persisted official site record
- **THEN** the system SHALL still perform the external search using the artist name
- **AND** return a list of upcoming concerts if found
- **AND** NOT return an error solely because the official site is missing

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system must filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system returns an empty list without error

#### Scenario: Error context in failures

- **WHEN** any internal operation fails (get artist, list existing concerts, search external API)
- **THEN** the error SHALL be wrapped with `fmt.Errorf` indicating which step failed
- **AND** the original error SHALL be preserved via `%w` verb

### Requirement: Concert Persistence

The system SHALL route any new concert discovered via the search mechanism into the approval queue
rather than persisting it directly. A discovered concert SHALL be staged in `pending` state and
SHALL be inserted into the published `events`/`concerts`/`series`/`event_performers` tables only
when a developer approves it. The `ConcertRepository.Create` method SHALL remain the persistence
path used at approval time: it SHALL accept a variadic number of concerts for bulk insert support
and SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Discovered concerts are staged, not persisted

- **WHEN** `SearchNewConcerts` finds concerts not currently in the database
- **THEN** those concerts SHALL be staged in the approval queue in `pending` state
- **AND** they SHALL NOT be inserted into the `events`/`concerts` tables until approved

#### Scenario: Persist on approval

- **WHEN** a developer approves a pending staged concert
- **THEN** the concert SHALL be saved to the persisted storage via a single bulk insert call
- **AND** persisted with a valid ID

#### Scenario: Persist Venues on approval

- **WHEN** a staged concert is approved and its resolved venue does not exist in the database
- **THEN** a new venue is created based on the resolved venue from staging
- **AND** if an `admin_area` was extracted for the concert, it SHALL be stored on the venue record
- **AND** the new venue SHALL have `enrichment_status` set to `'pending'`
- **AND** the approved concert is associated with this new venue

#### Scenario: Bulk insert uses unnest

- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction
- **AND** no `maxConcertsPerBatch` batching loop SHALL be required

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation
