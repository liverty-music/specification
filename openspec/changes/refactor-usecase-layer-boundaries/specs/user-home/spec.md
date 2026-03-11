## MODIFIED Requirements

### Requirement: User Home Area Data Model

The system SHALL support a structured `home` field on the User entity representing the user's home area — the geographic area where the user regularly attends live events without considering it a "trip" (遠征). The value is a structured geographic location expressed through a hierarchy of internationally standardized codes, with centroid coordinates for proximity calculations.

#### Scenario: Home message in Proto definition

- **WHEN** the `Home` proto message is defined
- **THEN** it SHALL contain a `string country_code` field validated as ISO 3166-1 alpha-2 (exactly two uppercase Latin letters, e.g., `JP`, `US`)
- **AND** a `string level_1` field validated as ISO 3166-2 format (4–6 characters, e.g., `JP-13`, `US-NY`)
- **AND** an `optional string level_2` field for finer-grained subdivision (1–20 characters when present)
- **AND** an `optional double centroid_latitude` field for the centroid latitude
- **AND** an `optional double centroid_longitude` field for the centroid longitude

#### Scenario: Home field in database

- **WHEN** the `homes` table is defined
- **THEN** it SHALL include a primary key `id TEXT`
- **AND** a required `country_code TEXT` column storing an ISO 3166-1 alpha-2 code
- **AND** a required `level_1 TEXT` column storing an ISO 3166-2 subdivision code
- **AND** a nullable `level_2 TEXT` column storing a country-specific finer area code
- **AND** a nullable `centroid_latitude DOUBLE PRECISION` column for the centroid latitude
- **AND** a nullable `centroid_longitude DOUBLE PRECISION` column for the centroid longitude

#### Scenario: Home field in Go entity

- **WHEN** the Go `entity.Home` struct is defined
- **THEN** it SHALL include `ID string`, `CountryCode string`, `Level1 string`, `Level2 *string`, `Latitude float64`, and `Longitude float64` fields
- **AND** the `entity.User` struct SHALL include a `Home *Home` field
- **AND** a nil `Home` SHALL mean the user has not set their home area

#### Scenario: Centroid populated at write time

- **WHEN** `UserRepository.Create` or `UserRepository.UpdateHome` is called with a `Home` value
- **THEN** the repository implementation SHALL resolve the `Level1` ISO 3166-2 code to centroid coordinates
- **AND** store the resolved `centroid_latitude` and `centroid_longitude` alongside the other home fields
- **AND** the centroid resolution logic SHALL be an infrastructure implementation detail (not visible to usecase/entity layers)

#### Scenario: Code system contract for level_2

- **WHEN** `level_2` is populated
- **THEN** its code system SHALL be determined by `country_code`:
  - `JP` → future use (not yet defined; Phase 1 always omits level_2)
  - `US` → FIPS county code (e.g., `06037` for Los Angeles County)
  - `DE` → AGS code (e.g., `09162` for Munich)
- **AND** additional country mappings SHALL be documented in the `Home` proto message comment as they are introduced
