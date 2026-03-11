## MODIFIED Requirements

### Requirement: Proximity Classification Model

The system SHALL classify the geographic relationship between a user's home area and a concert venue into one of three proximity levels: HOME, NEARBY, or AWAY. Classification SHALL be performed by the `Concert.ProximityTo(home)` entity method using centroid coordinates stored on the `Home` entity as a `*Coordinates` value.

#### Scenario: HOME classification by admin_area match

- **WHEN** the venue's `admin_area` matches the user's `home.Level1` (ISO 3166-2 code equality)
- **THEN** the venue SHALL be classified as HOME

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** the venue's `admin_area` does not match the user's `home.Level1`
- **AND** the venue has coordinates (`Venue.Coordinates` is non-nil)
- **AND** the user's home has a centroid (`Home.Centroid` is non-nil)
- **AND** the Haversine distance between `Home.Centroid` and `Venue.Coordinates` is less than or equal to 200km
- **THEN** the venue SHALL be classified as NEARBY

#### Scenario: AWAY classification for distant venues

- **WHEN** the venue has coordinates (`Venue.Coordinates` is non-nil)
- **AND** the venue's `admin_area` does **not** match the user's `home.Level1`
- **AND** the Haversine distance between `Home.Centroid` and `Venue.Coordinates` exceeds 200km
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification for venues without coordinates

- **WHEN** the venue does not have coordinates (`Venue.Coordinates` is nil)
- **AND** the venue's `admin_area` does not match the user's `home.Level1`
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification when user has no home

- **WHEN** the user has not set a home area (home is nil)
- **THEN** all venues SHALL be classified as AWAY

### Requirement: Home Area Centroid Lookup

The system SHALL resolve geographic centroid coordinates for the user's home area at write time (when `UpdateHome` or `Create` is called) and store them on the `homes` table. The centroid lookup is an infrastructure implementation detail — the entity and usecase layers access centroids via `Home.Centroid`.

#### Scenario: Centroid resolved at home write time

- **WHEN** a user sets or updates their home area via `UpdateHome` or `Create`
- **THEN** the repository layer SHALL resolve the `level_1` ISO 3166-2 code to centroid coordinates
- **AND** store the centroid as `centroid_latitude` and `centroid_longitude` on the `homes` table row

#### Scenario: Japanese prefecture centroid resolution

- **WHEN** a home area is set with a Japanese ISO 3166-2 code (e.g., `JP-13`)
- **THEN** the repository SHALL resolve it to the prefecture's approximate geographic centroid

#### Scenario: Unsupported country code centroid

- **WHEN** a home area is set with an unsupported country's ISO 3166-2 code
- **THEN** the centroid columns SHALL be set to NULL
- **AND** `Home.Centroid` SHALL be nil
- **AND** `Concert.ProximityTo()` SHALL treat nil centroids as AWAY (no NEARBY classification possible)

#### Scenario: Existing rows backfilled

- **WHEN** the centroid columns migration is applied
- **THEN** all existing `homes` rows with Japanese ISO 3166-2 codes SHALL be backfilled with centroid coordinates

### Requirement: Centroid Resolution Unit Coverage

The infrastructure centroid resolution logic SHALL be independently testable and tested.

#### Scenario: Japanese prefecture centroid lookup

- **WHEN** `ResolveCentroid` is called with a valid Japanese ISO 3166-2 code (e.g., `JP-13`)
- **THEN** it SHALL return coordinates with `ok = true`
- **AND** the latitude and longitude SHALL match the expected centroid for that prefecture

#### Scenario: Unsupported region code

- **WHEN** `ResolveCentroid` is called with an unsupported ISO 3166-2 code (e.g., `US-NY`)
- **THEN** it SHALL return `ok = false`
- **AND** the caller SHALL treat the coordinates as absent
