## Purpose

Stores the record of a passkey that finished registration for a User, so its provider and registration time can be shown later.

## ADDED Requirements

### Requirement: Create is idempotent on the provider passkey id

Create SHALL store a Passkey with the given provider passkey id, User, AAGUID and create time. When a Passkey with the same provider passkey id already exists, Create SHALL succeed and leave the stored Passkey unchanged. It SHALL fail with NotFound when the User does not exist.

#### Scenario: New passkey

- **WHEN** Create runs for a provider passkey id that has no Passkey
- **THEN** the Passkey is stored with the given User, AAGUID and create time

#### Scenario: Same passkey again

- **WHEN** Create runs again for a provider passkey id that already has a Passkey
- **THEN** it succeeds and the stored Passkey is unchanged

#### Scenario: Unknown User

- **WHEN** Create runs for a User that does not exist
- **THEN** it fails with NotFound and nothing is stored
