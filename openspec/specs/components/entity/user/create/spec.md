# User.Create

## Purpose

Stores a new User, together with its Home when one is supplied, and returns the stored User.

## Requirements

### Requirement: Create stores the user and its home together

Create SHALL store the new User and, when a Home is supplied, that Home linked to the User, together or not at all. The returned User SHALL carry the fresh id and, when a Home was supplied, the stored Home. A User created without a Home SHALL have no home.

#### Scenario: Create with a home

- **WHEN** Create runs with a Home of country code `JP` and level 1 `JP-13`
- **THEN** the User and its Home are stored and the returned User carries that Home

#### Scenario: Create without a home

- **WHEN** Create runs without a Home
- **THEN** the User is stored with no home

#### Scenario: Storing the home fails

- **WHEN** the Home cannot be stored
- **THEN** Create fails and no User is stored

### Requirement: Create sets the home's centroid

When Create stores a Home, it SHALL set the Home's centroid to the centre of its level 1 area when that area is in the supported catalog (the 47 Japanese prefectures), and SHALL leave the centroid absent otherwise.

#### Scenario: Japanese prefecture

- **WHEN** Create stores a Home with level 1 `JP-13`
- **THEN** the stored Home carries the centroid of Tokyo

#### Scenario: Area outside the catalog

- **WHEN** Create stores a Home with level 1 `US-CA`
- **THEN** the stored Home has no centroid

### Requirement: Create rejects a taken identity or email

Create SHALL fail with AlreadyExists and store nothing when another User already has the same external id or the same email.

#### Scenario: Same external id

- **WHEN** a User with the same external id already exists
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Same email

- **WHEN** a User with a different external id already has the same email
- **THEN** Create fails with AlreadyExists and stores nothing

### Requirement: Absent preferred language is stored absent

When Create runs without a preferred language, the stored User SHALL have no preferred language.

#### Scenario: No preferred language

- **WHEN** Create runs without a preferred language
- **THEN** the stored User has no preferred language
