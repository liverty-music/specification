## MODIFIED Requirements

### Requirement: A removed Passkey is announced as removed

When Delete removes a Passkey, it SHALL announce the Passkey as removed (Passkey.Removed), carrying the Passkey as it was stored, together with the removal: both are stored or neither is. When the announcement cannot be recorded, Delete SHALL fail with Unavailable and the Passkey SHALL stay stored.

#### Scenario: Passkey removed

- **WHEN** Delete removes the Passkey of a User
- **THEN** one removed Passkey is announced, carrying its provider passkey id, User, provider name (looked up from its AAGUID), name and create time

#### Scenario: Announcement cannot be recorded

- **WHEN** Delete would remove a Passkey and the announcement cannot be recorded
- **THEN** Delete fails with Unavailable and the Passkey is still stored
