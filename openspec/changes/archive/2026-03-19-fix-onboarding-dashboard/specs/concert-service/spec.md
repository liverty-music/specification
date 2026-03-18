## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Venue Resolution in Concert List

The `ConcertRepository.ListByArtist` implementation SHALL JOIN the `venues` table so that every returned `Concert` carries a populated `Venue` with `name` and `admin_area`. Additionally, a new `ListByArtists` (plural) repository method SHALL support querying multiple artists in a single SQL call with venue coordinates included.

#### Scenario: Venue JOIN in list query

- **WHEN** `ListByArtist` is called
- **THEN** the SQL query SHALL JOIN `events` and `venues` tables
- **AND** `venue.name` and `venue.admin_area` SHALL be scanned into the returned entities

#### Scenario: Concert mapper includes Venue

- **WHEN** a `Concert` entity is mapped to proto
- **THEN** `ConcertToProto` SHALL populate the `venue` field using `VenueToProto`
- **AND** SHALL populate `listed_venue_name` from `Concert.Event.ListedVenueName`

#### Scenario: ListByArtists (plural) query with coordinates

- **WHEN** `ListByArtists` is called with a list of artist IDs
- **THEN** the SQL query SHALL use `WHERE c.artist_id = ANY($1)` to filter by multiple artists
- **AND** the query SHALL include `v.latitude, v.longitude` in the SELECT for proximity calculation
- **AND** the query SHALL order results by `e.local_event_date ASC`
