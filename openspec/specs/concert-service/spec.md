# concert-service Specification

## Purpose

The Concert Service manages the lifecycle of concert data, including artist management, automated discovery via search, and persistent storage of concert and venue information.

## Requirements

### Requirement: Concert Service

The system SHALL provide a gRPC service to manage concerts and artists.

#### Scenario: List Concerts by Artist

- **WHEN** `List` is called with a valid `artist_id`
- **THEN** it returns a list of concerts associated with that artist
- **AND** each concert SHALL include an `EventId` (not `ConcertId`) as its identifier
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

### Requirement: List Concerts with Proximity for Unauthenticated Users

The system SHALL provide a public RPC `ListWithProximity` that accepts a list of artist IDs and a Home, returning concerts grouped by date and classified by proximity. This RPC does not require authentication and shares the same `GroupByDateAndProximity` logic as `ListByFollower`.

#### Scenario: Successful proximity-grouped listing

- **WHEN** `ListWithProximity` is called with one or more `artist_ids` and a valid `Home` (country_code + level_1)
- **THEN** it SHALL return concerts grouped by date using `ProximityGroup` messages
- **AND** each `ProximityGroup` SHALL contain concerts classified into `home`, `nearby`, and `away` fields based on `Concert.ProximityTo(home)`
- **AND** each concert SHALL include a resolved `Venue` object with `name`, `admin_area`, and coordinates
- **AND** each concert SHALL include `listed_venue_name` with the raw scraped venue name
- **AND** groups SHALL be ordered by date ascending

#### Scenario: Home centroid resolved server-side

- **WHEN** `ListWithProximity` is called with `Home.level_1` (e.g., "JP-40")
- **THEN** the backend SHALL resolve the centroid from `level_1` using `geo.ResolveCentroid()`
- **AND** the resolved centroid SHALL be used for Haversine distance calculation in proximity classification

#### Scenario: Empty artist list

- **WHEN** `ListWithProximity` is called with an empty `artist_ids` list
- **THEN** it SHALL return an `INVALID_ARGUMENT` error

#### Scenario: No concerts found for any artist

- **WHEN** `ListWithProximity` is called with valid artist IDs
- **AND** no concerts exist for any of the specified artists
- **THEN** it SHALL return an empty `groups` list without error

#### Scenario: Artist ID validation limit

- **WHEN** `ListWithProximity` is called with more than 50 artist IDs
- **THEN** it SHALL return an `INVALID_ARGUMENT` error via protovalidate

#### Scenario: Home with unsupported country code

- **WHEN** `ListWithProximity` is called with a `Home` whose `level_1` has no known centroid
- **THEN** the centroid SHALL be nil
- **AND** all concerts SHALL be classified as `AWAY` (except those matching by `admin_area`)

### Requirement: Venue Resolution in Concert List

The `ConcertRepository.ListByArtist` implementation SHALL JOIN the `venues` table so that every returned `Concert` carries a populated `Venue` with `name` and `admin_area`. Additionally, a new `ListByArtists` (plural) repository method SHALL support querying multiple artists in a single SQL call with venue coordinates included.

#### Scenario: Venue JOIN in list query

- **WHEN** `ListByArtist` is called
- **THEN** the SQL query SHALL JOIN `events` and `venues` tables
- **AND** `venue.name` and `venue.admin_area` SHALL be scanned into the returned entities

#### Scenario: Concert mapper includes Venue

- **WHEN** a `Concert` entity is mapped to proto
- **THEN** `ConcertToProto` SHALL populate the `id` field using `EventId` (not `ConcertId`)
- **AND** SHALL populate the `venue` field using `VenueToProto`
- **AND** SHALL populate `listed_venue_name` from `Concert.Event.ListedVenueName`

#### Scenario: ListByArtists (plural) query with coordinates

- **WHEN** `ListByArtists` is called with a list of artist IDs
- **THEN** the SQL query SHALL use `WHERE c.artist_id = ANY($1)` to filter by multiple artists
- **AND** the query SHALL include `v.latitude, v.longitude` in the SELECT for proximity calculation
- **AND** the query SHALL order results by `e.local_event_date ASC`

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

The system SHALL provide an RPC to retrieve all concerts for artists followed by the authenticated user, grouped by date and classified by proximity.

#### Scenario: Authenticated user with followed artists

- **WHEN** `ListByFollower` is called by an authenticated user who follows one or more artists
- **THEN** it SHALL return concerts grouped by date using `ProximityGroup` messages
- **AND** each `ProximityGroup` SHALL contain concerts classified into `home`, `nearby`, and `away` fields based on `Concert.ProximityTo(user.Home)`
- **AND** each concert SHALL include a resolved `Venue` object with `name` and `admin_area` if available
- **AND** each concert SHALL include `listed_venue_name` with the raw scraped venue name
- **AND** groups SHALL be ordered by date ascending

#### Scenario: Authenticated user with no followed artists

- **WHEN** `ListByFollower` is called by an authenticated user who follows no artists
- **THEN** it SHALL return an empty list without error

#### Scenario: Unauthenticated caller

- **WHEN** `ListByFollower` is called without valid authentication
- **THEN** it SHALL return an `UNAUTHENTICATED` error

#### Scenario: ProximityGroup field structure

- **WHEN** a `ProximityGroup` message is defined in proto
- **THEN** it SHALL contain a required `date` field of type `entity.v1.LocalDate`
- **AND** a `repeated entity.v1.Concert home` field for home-proximity concerts
- **AND** a `repeated entity.v1.Concert nearby` field for nearby-proximity concerts
- **AND** a `repeated entity.v1.Concert away` field for away-proximity concerts

#### Scenario: Single SQL query execution

- **WHEN** `ListByFollower` is called
- **THEN** the backend SHALL execute a single SQL query joining `concerts`, `events`, `venues`, and `followed_artists` tables
- **AND** the query SHALL filter by the authenticated user's internal ID

### Requirement: Event Natural Key Constraint

The `events` table SHALL have a composite UNIQUE constraint on the natural key `(venue_id, local_event_date, start_at)` to prevent duplicate event rows at the database level. This constraint serves as the final safety net when application-level dedup fails.

#### Scenario: Duplicate event insert is rejected

- **WHEN** a concert is inserted with the same `(venue_id, local_event_date, start_at)` as an existing event
- **THEN** the database SHALL reject the insert via the UNIQUE constraint
- **AND** the application SHALL handle this gracefully via UPSERT (not error)

#### Scenario: NULL-safe equality for start_at in constraint

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** both have `start_at = NULL`
- **THEN** the UNIQUE constraint SHALL treat them as duplicates
- **AND** the constraint SHALL use a `UNIQUE NULLS NOT DISTINCT` clause or a partial unique index to handle NULL equality

#### Scenario: Same venue and date with different start_at

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** different non-NULL `start_at` values
- **THEN** the UNIQUE constraint SHALL allow both rows (matinee/evening shows)

### Requirement: Concert UPSERT on Natural Key

The `ConcertRepository.Create` bulk insert SHALL use `ON CONFLICT` on the natural key to perform an UPSERT. When a conflict is detected, the existing record's `open_at` SHALL be updated if the new value provides previously unknown information. Since `start_at` is part of the natural key, a conflict implies both rows have the same `start_at` value (including both NULL); therefore `start_at` updates happen via new row insertion, not UPSERT update.

#### Scenario: Insert new event (no conflict)

- **WHEN** `Create` is called with a concert whose natural key does not exist
- **THEN** the event SHALL be inserted normally

#### Scenario: Different start_at inserts new row (not UPSERT)

- **WHEN** `Create` is called with a concert at the same `(venue_id, local_event_date)` as an existing event
- **AND** the `start_at` values differ (e.g., existing is NULL, new is non-NULL; or both are non-NULL but different instants)
- **THEN** the natural keys are distinct and no conflict occurs
- **AND** the new concert SHALL be inserted as a separate event row

#### Scenario: Conflict with richer open_at — update existing

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event has `open_at = NULL`
- **AND** the new concert has a non-NULL `open_at`
- **THEN** the existing event's `open_at` SHALL be updated to the new value via `COALESCE(EXCLUDED.open_at, events.open_at)`

#### Scenario: Conflict does not overwrite existing non-NULL open_at with NULL

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event already has a non-NULL `open_at`
- **AND** the new concert has `open_at = NULL`
- **THEN** the existing event's `open_at` SHALL NOT be overwritten
- **AND** SHALL retain its current value via `COALESCE(NULL, events.open_at)`

#### Scenario: Concerts row skipped for UPSERTed events with different UUID

- **WHEN** `Create` is called with a concert whose event UUID differs from the existing event at the same natural key
- **THEN** the events UPSERT SHALL update the existing row (keeping the original UUID)
- **AND** the input UUID SHALL NOT exist in the `events` table
- **AND** the `concerts` INSERT SHALL skip this row via `WHERE EXISTS` (no duplicate concerts row created)

### Requirement: Duplicate Data Cleanup Migration

A one-time database migration SHALL remove duplicate event rows created by the bug, retaining only the earliest-inserted row per natural key.

#### Scenario: Dedup retains earliest event per natural key

- **WHEN** the migration runs
- **AND** multiple events share the same `(venue_id, local_event_date, start_at)` (NULL-safe)
- **THEN** only the event with the smallest `id` (earliest UUIDv7 timestamp) SHALL be retained
- **AND** all other duplicates SHALL be deleted
- **AND** corresponding `concerts` rows for deleted events SHALL be cascade-deleted

#### Scenario: Migration is idempotent

- **WHEN** the migration is run on a database with no duplicates
- **THEN** no rows SHALL be deleted
- **AND** the migration SHALL complete without error

#### Scenario: UNIQUE constraint applied after cleanup

- **WHEN** the migration runs
- **THEN** it SHALL first delete duplicates
- **AND** then add the UNIQUE constraint
- **AND** the constraint addition SHALL succeed because duplicates have been removed

### Requirement: ConcertService handler timeout isolation

The ConcertService RPC handlers SHALL have a dedicated handler timeout of 120 seconds, separate from the default handler timeout applied to other services. This accommodates the Gemini API + Google Search grounding response time (25-110 seconds).

#### Scenario: SearchNewConcerts completes within 120 seconds

- **WHEN** `SearchNewConcerts` is called and the Gemini API responds within 120 seconds
- **THEN** the RPC SHALL return successfully with discovered concerts

#### Scenario: SearchNewConcerts exceeds 120 seconds

- **WHEN** `SearchNewConcerts` is called and the handler timeout of 120 seconds is exceeded
- **THEN** the RPC SHALL return a deadline exceeded error to the client

#### Scenario: Other services retain default timeout

- **WHEN** an RPC on UserService or ArtistService is called
- **THEN** the default handler timeout (60 seconds) SHALL apply
- **AND** the ConcertService timeout SHALL NOT affect other services

### Requirement: GKE Gateway timeout for ConcertService

The GKE Gateway backend policy `timeoutSec` SHALL be set to 150 seconds to accommodate the ConcertService handler timeout (120 seconds) plus network overhead buffer.

#### Scenario: Gateway timeout exceeds handler timeout

- **WHEN** a request is routed through the GKE Gateway to the backend
- **THEN** the Gateway timeout (150 seconds) SHALL be greater than the ConcertService handler timeout (120 seconds)
- **AND** the Gateway SHALL NOT prematurely terminate ConcertService requests
