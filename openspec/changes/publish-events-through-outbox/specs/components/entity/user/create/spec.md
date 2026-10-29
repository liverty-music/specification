## ADDED Requirements

### Requirement: A created User is announced with it

When Create stores a new User, it SHALL announce the created User together with it: both are stored or neither is. The announcement SHALL carry the User with its id, provider user ID and email address, and SHALL NOT carry its full name or phone number. When Create fails with AlreadyExists, it SHALL announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and no User SHALL be stored.

#### Scenario: New user

- **WHEN** Create stores a User for provider user ID `abc` and email `fan@example.com`
- **THEN** one created User is announced, carrying its id, provider user ID `abc` and email `fan@example.com`

#### Scenario: Identity already registered

- **WHEN** Create fails with AlreadyExists because a User with the same provider user ID exists
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store a new User and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no User is stored
