## MODIFIED Requirements

### Requirement: Create rejects a taken identity or email

Create SHALL fail with AlreadyExists and store nothing when another User already has the same provider user ID or the same email. Two emails SHALL be the same when they are equal with letter case ignored. Create SHALL store the email as given, in its own letter case.

#### Scenario: Same provider user ID

- **WHEN** a User with the same provider user ID already exists
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Same email

- **WHEN** a User with a different provider user ID already has the same email
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Same email in another letter case

- **WHEN** a User with a different provider user ID has the email `fan@example.com` and Create runs with `Fan@Example.com`
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Letter case kept

- **WHEN** Create stores a new User with the email `Fan@Example.com`
- **THEN** the stored User's email is `Fan@Example.com`
