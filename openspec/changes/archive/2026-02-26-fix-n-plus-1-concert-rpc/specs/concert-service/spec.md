## ADDED Requirements

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
