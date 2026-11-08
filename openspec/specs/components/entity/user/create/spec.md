# User.Create

## Purpose

Stores a new User together with its Home and returns the stored User.

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

Create SHALL fail with AlreadyExists and store nothing when another User already has the same provider user ID or the same email.

#### Scenario: Same provider user ID

- **WHEN** a User with the same provider user ID already exists
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Same email

- **WHEN** a User with a different provider user ID already has the same email
- **THEN** Create fails with AlreadyExists and stores nothing

### Requirement: A created User is announced with it

When Create stores a new User, it SHALL announce the created User together with it: both are stored or neither is. The announcement SHALL carry the User with its id, provider user ID and email address, and SHALL NOT carry its full name, phone number or the display name given by the identity provider. When Create fails with AlreadyExists, it SHALL announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and no User SHALL be stored.

#### Scenario: New user

- **WHEN** Create stores a User for provider user ID `abc` and email `fan@example.com`
- **THEN** one created User is announced, carrying its id, provider user ID `abc` and email `fan@example.com`, and none of its full name, phone number and display name

#### Scenario: Identity already registered

- **WHEN** Create fails with AlreadyExists because a User with the same provider user ID exists
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store a new User and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no User is stored
