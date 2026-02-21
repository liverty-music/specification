## MODIFIED Requirements

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

## ADDED Requirements

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
