## MODIFIED Requirements

### Requirement: List Concerts with Proximity for Unauthenticated Users

The system SHALL provide a public RPC `ListWithProximity` that accepts a list of artist IDs and a Home, returning concerts grouped by date and classified by proximity. This RPC does not require authentication and shares the same `GroupByDateAndProximity` logic as `ListByFollower`. The backend auth interceptor SHALL include `ListWithProximity` in its public method whitelist so that requests without a bearer token are accepted.

#### Scenario: Unauthenticated guest calls ListWithProximity

- **WHEN** `ListWithProximity` is called without an `Authorization` header (e.g., during onboarding as a guest user)
- **THEN** the auth interceptor SHALL allow the request through without returning `UNAUTHENTICATED`
- **AND** the RPC SHALL return proximity-grouped concerts normally

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
