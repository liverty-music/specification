# concert-service Specification

## Purpose

The Concert Service manages the lifecycle of concert data, including artist management, automated discovery via search, and persistent storage of concert and venue information.

## Requirements

### Requirement: Concert Service

The system SHALL provide a gRPC service to manage concerts and artists.

#### Scenario: List Concerts by Artist

- **WHEN** `List` is called with a valid `artist_id`
- **THEN** it returns a list of concerts associated with that artist
- **AND** each concert SHALL include a resolved `Venue` object with `name` and `admin_area` if available
- **AND** each concert SHALL include `listed_venue_name` with the raw scraped venue name
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

#### Scenario: Successful Search with known official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has a persisted official site record
- **THEN** the system returns a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database

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

The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support. The bulk insert SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Persist New Concerts

- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Persist Venues

- **WHEN** a discovered concert has a venue that does not exist in the database
- **THEN** a new venue is created dynamically based on the listed venue name provided by the source
- **AND** if an `admin_area` was extracted for the concert, it SHALL be stored on the venue record
- **AND** the new venue SHALL have `enrichment_status` set to `'pending'`
- **AND** the new concert is associated with this new venue

#### Scenario: Bulk insert uses unnest

- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction
- **AND** no `maxConcertsPerBatch` batching loop SHALL be required

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to the previous single-insert implementation

### Requirement: Venue Resolution in Concert List

The `ConcertRepository.ListByArtist` implementation SHALL JOIN the `venues` table so that every returned `Concert` carries a populated `Venue` with `name` and `admin_area`.

#### Scenario: Venue JOIN in list query

- **WHEN** `ListByArtist` is called
- **THEN** the SQL query SHALL JOIN `events` and `venues` tables
- **AND** `venue.name` and `venue.admin_area` SHALL be scanned into the returned entities

#### Scenario: Concert mapper includes Venue

- **WHEN** a `Concert` entity is mapped to proto
- **THEN** `ConcertToProto` SHALL populate the `venue` field using `VenueToProto`
- **AND** SHALL populate `listed_venue_name` from `Concert.Event.ListedVenueName`

### Requirement: Concert-Event Association

Every Concert entity SHALL be securely linked to a distinct generic Event entity.

#### Scenario: Concert Data Integrity
- **WHEN** a Concert is persisted or retrieved
- **THEN** it MUST include all fields defined in the `Event` entity (Title, Date, Venue, etc.)
- **AND** data consistency between the Concert specific fields (ArtistID) and Event generic fields MUST be maintained

### Requirement: Listed Venue Name Preservation

The system SHALL preserve the raw venue name as found on the artist's official site on the Event record, separate from the normalized `Venue.Name`. This ensures the original source text is available for future normalization workflows (e.g., matching against Google Maps or MusicBrainz).

#### Scenario: Listed venue name stored on event creation

- **WHEN** a new concert event is persisted
- **THEN** the `listed_venue_name` field on the event SHALL contain the exact venue name string returned by the Gemini extraction

#### Scenario: Listed venue name is non-empty for discovered concerts

- **WHEN** Gemini returns a non-empty venue string for a concert
- **THEN** `listed_venue_name` on the persisted event SHALL be that string

### Requirement: Venue AdminArea Persistence

The system SHALL store the administrative area extracted by Gemini on the Venue record when available.

#### Scenario: AdminArea stored on new venue creation

- **WHEN** a new venue is created and the scraped concert includes a non-empty `admin_area`
- **THEN** the venue record SHALL have `admin_area` set to that value

#### Scenario: AdminArea is NULL when not extracted

- **WHEN** a new venue is created and the scraped concert has no `admin_area` (empty or absent)
- **THEN** the venue record SHALL have `admin_area` set to `NULL`

### Requirement: List Concerts by Follower

The system SHALL provide an RPC to retrieve all concerts for artists followed by the authenticated user in a single request.

#### Scenario: Authenticated user with followed artists

- **WHEN** `ListByFollower` is called by an authenticated user who follows one or more artists
- **THEN** it SHALL return all concerts associated with those followed artists
- **AND** each concert SHALL include a resolved `Venue` object with `name` and `admin_area` if available
- **AND** each concert SHALL include `listed_venue_name` with the raw scraped venue name
- **AND** concerts SHALL be ordered by `local_event_date` ascending

#### Scenario: Authenticated user with no followed artists

- **WHEN** `ListByFollower` is called by an authenticated user who follows no artists
- **THEN** it SHALL return an empty list without error

#### Scenario: Unauthenticated caller

- **WHEN** `ListByFollower` is called without valid authentication
- **THEN** it SHALL return an `UNAUTHENTICATED` error

#### Scenario: Single SQL query execution

- **WHEN** `ListByFollower` is called
- **THEN** the backend SHALL execute a single SQL query joining `concerts`, `events`, `venues`, and `followed_artists` tables
- **AND** the query SHALL filter by the authenticated user's internal ID
