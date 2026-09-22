# List By Artist

## Purpose

Lists concerts for a given artist with resolved venue information, and reports whether that artist has any upcoming live events.

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

### Requirement: Check whether an artist has upcoming live events

The system SHALL provide a mechanism to check whether an artist has upcoming live events by querying the `ConcertService/List` RPC. This replaces the previous hash-based mock implementation.

#### Scenario: Artist has upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns one or more concerts for that artist
- **THEN** the system SHALL return `true`

#### Scenario: Artist has no upcoming events

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** `ConcertService/List` returns an empty list
- **THEN** the system SHALL return `false`

#### Scenario: Concert list call fails

- **WHEN** `checkLiveEvents` is called with an artist ID
- **AND** the `ConcertService/List` RPC call fails
- **THEN** the system SHALL return `false`
- **AND** the system SHALL log the error
