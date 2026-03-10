## MODIFIED Requirements

### Requirement: Live Schedule Access

The system MUST provide access to the collected schedule of concerts.

#### Scenario: List Concerts

- **WHEN** `ListConcerts` is called for a valid artist ID
- **THEN** the system MUST return a chronologically sorted list of future concerts for that artist.

#### Scenario: List Concerts by Follower

- **WHEN** `ListByFollower` is called by an authenticated user
- **THEN** the system MUST return concerts for all artists followed by that user, grouped by date and classified into home/nearby/away lanes
- **AND** each group SHALL contain a calendar date and three concert lists (home, nearby, away)
- **AND** groups SHALL be ordered by date ascending
- **AND** lane classification SHALL be performed by the backend using the proximity classification model
- **AND** the result SHALL be retrieved in a single RPC call

### Requirement: Dashboard Lane Classification

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
