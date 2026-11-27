## MODIFIED Requirements

### Requirement: Create is get-or-create

Create SHALL store the Venue and return its id when no Venue holds its place id and no Venue holds its listed venue name with the same admin area. When one does, Create SHALL store nothing and return that Venue's id instead, including when a concurrent Create stored it first; it SHALL NOT fail with AlreadyExists.

#### Scenario: New venue
- **WHEN** no Venue holds the place id or the listed venue name and admin area
- **THEN** the Venue is stored and its id returned

#### Scenario: Place id already held
- **WHEN** a Venue with the same place id exists
- **THEN** Create returns the existing Venue's id and stores nothing

#### Scenario: Listed name and admin area already held
- **WHEN** a Venue with listed venue name "Zepp Osaka Bayside" and admin area JP-27 exists and another is created with the same pair and a different place id
- **THEN** Create returns the existing Venue's id

#### Scenario: Same listed name, different admin area
- **WHEN** a Venue lists "Zepp" in JP-13 and another listing "Zepp" in JP-27 is created
- **THEN** a second Venue is stored

#### Scenario: Concurrent create
- **WHEN** two Creates for the same place id run at once
- **THEN** both return the id of the one Venue stored

## ADDED Requirements

### Requirement: Create requires a first-level admin area and a time zone of its Area

Before looking for an existing Venue, Create SHALL fail with InvalidArgument and store nothing when the Venue has no admin area, its admin area is not the code of a first-level Area, it has no time zone, or its time zone is not one a Venue in that Area may have (see Venue, "Time zone of a venue": the Area's own time zone when it has one, otherwise one of its country's).

#### Scenario: No admin area
- **WHEN** Create runs for a Venue without an admin area
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Lower-level code
- **WHEN** Create runs for a Venue with admin area FR-33
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: No time zone
- **WHEN** Create runs for a Venue with admin area JP-13 and no time zone
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Time zone of another country
- **WHEN** Create runs for a Venue with admin area JP-13 and time zone Asia/Seoul
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Time zone other than the Area's own
- **WHEN** Create runs for a Venue with admin area US-CA and time zone America/New_York
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Venue abroad
- **WHEN** Create runs for a new Venue with admin area KR-11 and time zone Asia/Seoul
- **THEN** the Venue is stored with that admin area and time zone

### Requirement: Create stores coordinates with their fetch time

Create SHALL store a new Venue's coordinates together with the fetch time given with them, and SHALL fail with InvalidArgument and store nothing when coordinates are given without a fetch time. A Venue given no coordinates SHALL be stored with neither.

#### Scenario: Coordinates with their fetch time
- **WHEN** a new Venue is created with coordinates fetched at 2026-11-24 04:00 UTC
- **THEN** the Venue is stored with those coordinates and that fetch time

#### Scenario: Coordinates without a fetch time
- **WHEN** a new Venue is created with coordinates and no fetch time
- **THEN** Create fails with InvalidArgument and nothing is stored
