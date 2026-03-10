## ADDED Requirements

### Requirement: Proximity Classification Model

The system SHALL classify the geographic relationship between a user's home area and a concert venue into one of three lanes: HOME, NEARBY, or AWAY.

#### Scenario: HOME classification by admin_area match

- **WHEN** the venue's `admin_area` matches the user's `home.level_1` (ISO 3166-2 code equality)
- **THEN** the venue SHALL be classified as HOME

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** the venue's `admin_area` does not match the user's `home.level_1`
- **AND** the venue has latitude and longitude coordinates
- **AND** the user's home area has a known centroid
- **AND** the Haversine distance between the home centroid and the venue coordinates is less than or equal to 200km
- **THEN** the venue SHALL be classified as NEARBY

#### Scenario: AWAY classification for distant venues

- **WHEN** the venue has latitude and longitude coordinates
- **AND** the venue's `admin_area` does **not** match the user's `home.level_1`
- **AND** the Haversine distance between the home centroid and the venue coordinates exceeds 200km
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification for venues without coordinates

- **WHEN** the venue does not have latitude or longitude coordinates
- **AND** the venue's `admin_area` does not match the user's `home.level_1`
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification when user has no home

- **WHEN** the user has not set a home area
- **THEN** all venues SHALL be classified as AWAY

### Requirement: Home Area Centroid Lookup

The system SHALL maintain a lookup of geographic centroid coordinates for each supported ISO 3166-2 subdivision, used as the reference point for proximity calculations.

#### Scenario: Japanese prefecture centroid lookup

- **WHEN** a proximity calculation is performed for a user with a Japanese home area (e.g., `JP-13`)
- **THEN** the system SHALL resolve the ISO 3166-2 code to a latitude/longitude centroid for distance calculation

#### Scenario: Unsupported country code

- **WHEN** a proximity calculation is performed for a user with a home area in an unsupported country
- **THEN** the system SHALL treat all venues as AWAY (no proximity data available)

### Requirement: Haversine Distance Calculation

The system SHALL compute great-circle distance between two geographic points using the Haversine formula.

#### Scenario: Distance calculation accuracy

- **WHEN** the system calculates distance between Tokyo centroid (35.6895, 139.6917) and a venue at Saitama Super Arena (35.8950, 139.6314)
- **THEN** the result SHALL be approximately 23km (within 1km tolerance)

### Requirement: Venue Coordinate Storage

The system SHALL store latitude and longitude for venue records in the database, populated during the venue enrichment pipeline.

#### Scenario: Coordinates populated after enrichment

- **WHEN** a venue is successfully enriched via MusicBrainz or Google Places
- **AND** the external service response includes coordinates
- **THEN** the venue record SHALL be updated with latitude and longitude values

#### Scenario: Coordinates absent for unenriched venues

- **WHEN** a venue has `enrichment_status` of `pending` or `failed`
- **THEN** the venue's latitude and longitude SHALL be NULL
