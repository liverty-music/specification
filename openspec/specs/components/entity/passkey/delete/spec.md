# components/entity/passkey/delete Specification

## Purpose
Removes the record of a passkey that was removed at the identity provider, so a removed passkey is never shown with a provider or registration time.

## Requirements

### Requirement: Delete by provider passkey id is idempotent

Delete SHALL remove the Passkey with the given provider passkey id and SHALL succeed without change, announcing nothing, when none exists.

#### Scenario: Recorded passkey

- **WHEN** Delete runs for the provider passkey id of a stored Passkey
- **THEN** that Passkey is no longer stored

#### Scenario: Never recorded

- **WHEN** no Passkey has the provider passkey id
- **THEN** Delete succeeds and nothing is announced

### Requirement: A removed Passkey is announced as removed

When Delete removes a Passkey, it SHALL announce the Passkey as removed (Passkey.Removed), carrying the Passkey as it was stored, together with the removal: both are stored or neither is. When the announcement cannot be recorded, Delete SHALL fail with Unavailable and the Passkey SHALL stay stored.

#### Scenario: Passkey removed

- **WHEN** Delete removes the Passkey of a User
- **THEN** one removed Passkey is announced, carrying its provider passkey id, User, provider name (looked up from its AAGUID), name and create time

#### Scenario: Announcement cannot be recorded

- **WHEN** Delete would remove a Passkey and the announcement cannot be recorded
- **THEN** Delete fails with Unavailable and the Passkey is still stored
