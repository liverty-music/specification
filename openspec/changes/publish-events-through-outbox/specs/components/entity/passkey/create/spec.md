## MODIFIED Requirements

### Requirement: Create is idempotent on the provider passkey id

Create SHALL store a Passkey with the given provider passkey id, User, AAGUID, name and create time; the name is the label the identity provider gave the passkey, empty when it gave none. When a Passkey with the same provider passkey id already exists, Create SHALL succeed, leave the stored Passkey unchanged and announce nothing. It SHALL fail with NotFound when the User does not exist.

#### Scenario: New passkey

- **WHEN** Create runs for a provider passkey id that has no Passkey
- **THEN** the Passkey is stored with the given User, AAGUID, name and create time

#### Scenario: Same passkey again

- **WHEN** Create runs again for a provider passkey id that already has a Passkey
- **THEN** it succeeds, the stored Passkey is unchanged and nothing is announced

#### Scenario: Unknown User

- **WHEN** Create runs for a User that does not exist
- **THEN** it fails with NotFound and nothing is stored

## ADDED Requirements

### Requirement: A stored Passkey is announced as added

When Create stores a new Passkey, it SHALL announce the Passkey as added, carrying the stored Passkey, together with it: both are stored or neither is. When the announcement cannot be recorded, Create SHALL fail with Unavailable and no Passkey SHALL be stored.

#### Scenario: Passkey added

- **WHEN** Create stores a Passkey for a User
- **THEN** one added Passkey is announced, carrying its provider passkey id, User, AAGUID, name and create time

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store a new Passkey and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no Passkey is stored
