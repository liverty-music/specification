## RENAMED Requirements

### Requirement: DateLaneGroup → ProximityGroup

- **FROM**: `DateLaneGroup` message in `concert_service.proto`
- **TO**: `ProximityGroup` message in `concert_service.proto`

## MODIFIED Requirements

### Requirement: List Concerts by Follower

The system SHALL provide an RPC to retrieve all concerts for artists followed by the authenticated user, grouped by date and classified by proximity.

#### Scenario: Authenticated user with followed artists

- **WHEN** `ListByFollower` is called by an authenticated user who follows one or more artists
- **THEN** it SHALL return concerts grouped by date using `ProximityGroup` messages
- **AND** each `ProximityGroup` SHALL contain concerts classified into `home`, `nearby`, and `distant` fields based on `Concert.ProximityTo(user.Home)`
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
- **AND** a `repeated entity.v1.Concert distant` field for away-proximity concerts
