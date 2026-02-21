# concert-service Specification

## Purpose

The Concert Service manages the lifecycle of concert data, including artist management, automated discovery via search, and persistent storage of concert and venue information.

## Requirements

### Requirement: Concert Service

The system SHALL provide a gRPC service to manage concerts and artists.

#### Scenario: List Concerts by Artist

- **WHEN** `List` is called with a valid `artist_id`
- **THEN** it returns a list of concerts associated with that artist
- **AND** returns an empty list if no concerts are found (not an error)

#### Scenario: List All Artists

- **WHEN** `ListArtists` is called
- **THEN** it returns a list of all artists in the system

#### Scenario: Create Artist

- **WHEN** `CreateArtist` is called with a valid name
- **THEN** a new artist is created and returned with a generated ID
- **AND** the artist is persistable

#### Scenario: Create Artist with Invalid Name

- **WHEN** `CreateArtist` is called with an empty name
- **THEN** it returns an `INVALID_ARGUMENT` error

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. Error returns SHALL include contextual wrapping indicating which operation failed.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **THEN** the system returns a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system must filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system returns an empty list without error

#### Scenario: Error context in failures

- **WHEN** any internal operation fails (get artist, get official site, list existing concerts, search external API)
- **THEN** the error SHALL be wrapped with `fmt.Errorf` indicating which step failed
- **AND** the original error SHALL be preserved via `%w` verb

### Requirement: Concert Persistence

The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support. The bulk insert SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Persist New Concerts

- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Persist Venues

- **WHEN** a discovered concert has a venue that does not exist in the database
- **THEN** a new venue is created dynamically based on the name provided by the source
- **AND** the new concert is associated with this new venue

#### Scenario: Bulk insert uses unnest

- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction
- **AND** no `maxConcertsPerBatch` batching loop SHALL be required

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation

### Requirement: Concert-Event Association

Every Concert entity SHALL be securely linked to a distinct generic Event entity.

#### Scenario: Concert Data Integrity
- **WHEN** a Concert is persisted or retrieved
- **THEN** it MUST include all fields defined in the `Event` entity (Title, Date, Venue, etc.)
- **AND** data consistency between the Concert specific fields (ArtistID) and Event generic fields MUST be maintained
