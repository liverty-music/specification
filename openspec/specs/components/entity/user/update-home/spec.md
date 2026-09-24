# User.UpdateHome

## Purpose

Sets or replaces a User's Home and returns the updated User.

## Requirements

### Requirement: UpdateHome creates or replaces the home as a whole

UpdateHome SHALL give a User without a home a new Home, and SHALL replace every attribute of an existing Home with the supplied values while keeping its id. A level 2 omitted from the supplied Home SHALL leave the stored Home without level 2. The change SHALL be stored completely or not at all, and UpdateHome SHALL return the updated User.

#### Scenario: First home

- **WHEN** UpdateHome runs for a User with no home, with level 1 `JP-13`
- **THEN** the User has a new Home with level 1 `JP-13` and the returned User carries it

#### Scenario: Changing the home

- **WHEN** UpdateHome runs for a User whose home is `JP-13`, with level 1 `JP-27`
- **THEN** the User's Home keeps its id and now has level 1 `JP-27`

#### Scenario: Level 2 dropped

- **WHEN** the existing Home has a level 2 and the supplied Home has none
- **THEN** the stored Home has no level 2

### Requirement: UpdateHome sets the home's centroid

UpdateHome SHALL set the Home's centroid to the centre of its level 1 area when that area is in the supported catalog (the 47 Japanese prefectures), and SHALL leave the centroid absent otherwise, replacing any earlier centroid.

#### Scenario: Japanese prefecture

- **WHEN** UpdateHome stores a Home with level 1 `JP-27`
- **THEN** the stored Home carries the centroid of Osaka

#### Scenario: Area outside the catalog

- **WHEN** UpdateHome stores a Home with level 1 `US-CA` or a well-formed code not in the catalog such as `JP-99`
- **THEN** the stored Home has no centroid

### Requirement: UpdateHome on an unknown user

UpdateHome SHALL fail with NotFound and change nothing when no User has the given id, and with InvalidArgument when the id is empty.

#### Scenario: Unknown id

- **WHEN** no User has the given id
- **THEN** UpdateHome fails with NotFound and nothing is stored

#### Scenario: Empty id

- **WHEN** the id is empty
- **THEN** UpdateHome fails with InvalidArgument
