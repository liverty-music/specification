# List By Follower Grouped

## Purpose

Lists upcoming concerts for the artists a user follows, grouped by date and classified into home, nearby, and away lanes for display on their dashboard.

## Requirements

### Requirement: Dashboard Lane Assignment

The system SHALL assign concerts to one of three lanes — My City, My Region, Others — based on the concert's `venue.admin_area` relative to the user's stored region preference.

#### Scenario: Concert in user's city/prefecture

- **WHEN** a concert's `venue.admin_area` matches the user's stored region exactly
- **THEN** the concert SHALL be placed in the `main` (My City) lane

#### Scenario: Concert in a different prefecture

- **WHEN** a concert's `venue.admin_area` does not match the user's stored region
- **THEN** the concert SHALL be placed in the `other` lane

#### Scenario: Venue admin area not available

- **WHEN** a concert has no `venue.admin_area`
- **THEN** the concert SHALL be placed in the `other` lane

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

### Requirement: List concerts grouped by date for followed artists

The system MUST provide access to the collected schedule of concerts.

#### Scenario: List Concerts

- **WHEN** `ListConcerts` is called for a valid artist ID
- **THEN** the system MUST return a chronologically sorted list of future concerts for that artist.

#### Scenario: List Concerts by Follower

- **WHEN** `ListByFollower` is called by an authenticated user
- **THEN** the system MUST return concerts for all artists followed by that user, grouped by date and classified into home/nearby/away lanes
- **AND** by default (no `from` provided) the result SHALL include only concerts whose local event date is on or after the current date
- **AND** each group SHALL contain a calendar date and three concert lists (home, nearby, away)
- **AND** groups SHALL be ordered by date ascending
- **AND** lane classification SHALL be performed by the backend using the proximity classification model
- **AND** the result SHALL be retrieved in a single RPC call

#### Scenario: List Concerts by Follower from a given date

- **WHEN** `ListByFollower` is called with a `from` date
- **THEN** the system SHALL return concerts for the user's followed artists whose local event date is on or after `from`, including dates in the past when `from` is before the current date
- **AND** the grouping, lane classification, and date-ascending ordering SHALL be identical to the default call

#### Scenario: List Concerts by Follower with no matching concerts

- **WHEN** `ListByFollower` is called and no followed-artist concert falls on or after the effective start date
- **THEN** the system SHALL return an empty list of groups (not an error)

### Requirement: Classify concerts into home/nearby/away lanes

The backend SHALL classify live events into three lanes based on the proximity classification model, replacing the previous frontend-only classification.

#### Scenario: Home lane assignment

- **WHEN** a concert's venue `admin_area` matches the user's `home.level_1`
- **THEN** the concert SHALL be placed in the `home` list of its date group

#### Scenario: Nearby lane assignment

- **WHEN** a concert's venue has coordinates within 200km of the user's home centroid
- **AND** the venue `admin_area` does not match the user's `home.level_1`
- **THEN** the concert SHALL be placed in the `nearby` list of its date group

#### Scenario: Away lane assignment

- **WHEN** a concert's venue is beyond 200km, has no coordinates, or the user has no home set
- **THEN** the concert SHALL be placed in the `away` list of its date group

#### Scenario: User has no home set

- **WHEN** the user has not set a home area
- **THEN** all concerts SHALL be placed in the `away` list of their respective date groups
