## MODIFIED Requirements

### Requirement: Create stores the user and its home together

Create SHALL store the new User and its Home linked to the User, together or not at all. It SHALL fail with InvalidArgument and store nothing when no Home is supplied. The returned User SHALL carry the fresh id and the stored Home.

#### Scenario: Create with a home

- **WHEN** Create runs with a Home of country code `JP` and level 1 `JP-13`
- **THEN** the User and its Home are stored and the returned User carries that Home

#### Scenario: Create without a home

- **WHEN** Create runs without a Home
- **THEN** it fails with InvalidArgument and no User is stored

#### Scenario: Storing the home fails

- **WHEN** the Home cannot be stored
- **THEN** Create fails and no User is stored
