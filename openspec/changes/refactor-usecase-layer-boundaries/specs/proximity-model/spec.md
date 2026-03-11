## ADDED Requirements

### Requirement: Proximity Enum in Proto

The system SHALL define a `Proximity` enum in `entity/v1/proximity.proto` representing the geographic closeness between a user's home area and a concert venue. This enum is the canonical domain concept for proximity classification, symmetric with `HypeType`.

#### Scenario: Proximity enum definition

- **WHEN** the `Proximity` enum is defined in proto
- **THEN** it SHALL contain the values `PROXIMITY_UNSPECIFIED` (0), `PROXIMITY_HOME` (1), `PROXIMITY_NEARBY` (2), and `PROXIMITY_AWAY` (3)
- **AND** each value SHALL have a documentation comment explaining its meaning

#### Scenario: Symmetry with HypeType

- **WHEN** a user's `HypeType` is `HOME`
- **THEN** the corresponding proximity classification for notification filtering SHALL be `PROXIMITY_HOME`
- **AND** `HypeType.NEARBY` corresponds to `PROXIMITY_NEARBY`
- **AND** `HypeType.AWAY` corresponds to `PROXIMITY_AWAY`

### Requirement: Concert.ProximityTo Entity Method

The Go entity layer SHALL provide a `ProximityTo` receiver method on `Concert` that classifies the geographic relationship between the concert's venue and a user's home. This method SHALL be a pure function over entity fields with no infrastructure dependencies.

#### Scenario: HOME classification by admin_area match

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue `admin_area` matches `home.Level1`
- **THEN** the method SHALL return `ProximityHome`

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's `admin_area` does not match `home.Level1`
- **AND** the venue has latitude and longitude coordinates
- **AND** the Haversine distance between `(home.Latitude, home.Longitude)` and the venue coordinates is less than or equal to 200km
- **THEN** the method SHALL return `ProximityNearby`

#### Scenario: AWAY classification for distant venues

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the Haversine distance exceeds 200km
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue has no coordinates

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's latitude or longitude is nil
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when home is nil

- **WHEN** `Concert.ProximityTo(nil)` is called
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue is nil

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue is nil
- **THEN** the method SHALL return `ProximityAway`

### Requirement: Haversine in pkg/geo

The system SHALL provide a `Haversine` function in `pkg/geo` for computing great-circle distance between two WGS 84 coordinates. This is a pure math utility with no external dependencies, usable by any layer.

#### Scenario: Distance calculation

- **WHEN** `geo.Haversine` is called with Tokyo centroid (35.6895, 139.6917) and Saitama Super Arena (35.8950, 139.6314)
- **THEN** the result SHALL be approximately 23km (within 1km tolerance)
