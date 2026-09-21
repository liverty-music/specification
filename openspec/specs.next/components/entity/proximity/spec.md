# Proximity

## Purpose

Defines the proximity classification used to describe how close a concert's venue is to a user's home area, grouping and classifying concerts accordingly.

## Requirements

### Requirement: Concert proximity grouping

The entity package SHALL provide a `GroupByDateAndProximity(concerts []*Concert, home *Home) []*ProximityGroup` function that classifies concerts into Home/Nearby/Distant buckets grouped by calendar date.

Rules:
1. Concerts SHALL be grouped by `LocalDate` formatted as "YYYY-MM-DD".
2. Within each group, each concert SHALL be classified using `Concert.ProximityTo(home)`.
3. Groups SHALL be returned in the order of first appearance (preserving input date order).
4. An empty or nil input SHALL return nil.

#### Scenario: Empty input

- **WHEN** concerts slice is empty
- **THEN** function returns nil

#### Scenario: Single date, mixed proximity

- **WHEN** three concerts on 2026-03-15: one HOME, one NEARBY, one AWAY
- **THEN** returns one ProximityGroup with correct bucket assignments

#### Scenario: Multiple dates preserve order

- **WHEN** concerts span March 15, March 17, March 16 (in that input order)
- **THEN** returns three groups in order: March 15, March 17, March 16

#### Scenario: Nil home classifies all as Distant

- **WHEN** home is nil, concerts have venues
- **THEN** all concerts are placed in the Distant bucket

---

### Requirement: Concert proximity classification

The existing `Concert.ProximityTo(home *Home) Proximity` method SHALL classify a concert's geographic proximity to the user's home area.

Classification rules (evaluated in order):
1. AWAY — if `home` is nil or `Venue` is nil.
2. HOME — if venue's `AdminArea` matches `home.Level1`.
3. NEARBY — if venue has `Coordinates`, home has `Centroid`, and Haversine distance ≤ 200km.
4. AWAY — everything else.

#### Scenario: Nil home

- **WHEN** home is nil
- **THEN** returns ProximityAway

#### Scenario: Nil venue

- **WHEN** concert has no venue
- **THEN** returns ProximityAway

#### Scenario: Admin area match

- **WHEN** venue.AdminArea="JP-13" and home.Level1="JP-13"
- **THEN** returns ProximityHome

#### Scenario: Admin area mismatch with nearby coordinates

- **WHEN** venue.AdminArea="JP-14" (Kanagawa), home.Level1="JP-13" (Tokyo), venue is 30km from home centroid
- **THEN** returns ProximityNearby

#### Scenario: Admin area mismatch beyond threshold

- **WHEN** venue is 500km from home centroid, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Venue has no coordinates

- **WHEN** venue.Coordinates is nil, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Home has no centroid

- **WHEN** home.Centroid is nil, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Admin area match takes priority over distance

- **WHEN** venue.AdminArea matches home.Level1, even though distance > 200km
- **THEN** returns ProximityHome (admin area check runs first)

#### Scenario: Venue admin area is nil

- **WHEN** venue.AdminArea is nil, venue has coordinates within 200km of home
- **THEN** returns ProximityNearby

---

### Requirement: Classify a venue's proximity to the user's home

The system SHALL classify the geographic relationship between a user's home area and a concert venue into one of three proximity levels: HOME, NEARBY, or AWAY. Classification SHALL be performed by the `Concert.ProximityTo(home)` entity method using centroid coordinates stored on the `Home` entity.

#### Scenario: HOME classification by admin_area match

- **WHEN** the venue's `admin_area` matches the user's `home.Level1` (ISO 3166-2 code equality)
- **THEN** the venue SHALL be classified as HOME

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** the venue's `admin_area` does not match the user's `home.Level1`
- **AND** the venue has latitude and longitude coordinates
- **AND** the Haversine distance between the home centroid (`home.Latitude`, `home.Longitude`) and the venue coordinates is less than or equal to 200km
- **THEN** the venue SHALL be classified as NEARBY

#### Scenario: AWAY classification for distant venues

- **WHEN** the venue has latitude and longitude coordinates
- **AND** the venue's `admin_area` does **not** match the user's `home.Level1`
- **AND** the Haversine distance between the home centroid and the venue coordinates exceeds 200km
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification for venues without coordinates

- **WHEN** the venue does not have latitude or longitude coordinates
- **AND** the venue's `admin_area` does not match the user's `home.Level1`
- **THEN** the venue SHALL be classified as AWAY

#### Scenario: AWAY classification when user has no home

- **WHEN** the user has not set a home area (home is nil)
- **THEN** all venues SHALL be classified as AWAY

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
