## MODIFIED Requirements

### Requirement: A stored Passkey is announced as added

When Create stores a new Passkey, it SHALL announce the Passkey as added (Passkey.Added), carrying the stored Passkey, together with it: both are stored or neither is. When the announcement cannot be recorded, Create SHALL fail with Unavailable and no Passkey SHALL be stored.

#### Scenario: Passkey added

- **WHEN** Create stores a Passkey for a User
- **THEN** one added Passkey is announced, carrying its provider passkey id, User, provider name (looked up from its AAGUID), name and create time

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store a new Passkey and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no Passkey is stored
