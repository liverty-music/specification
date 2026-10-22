## Purpose

Lists the recorded passkeys of one User, so passkey management can show each passkey's provider and registration date.

## ADDED Requirements

### Requirement: ListByUser returns every recorded passkey of the User

ListByUser SHALL return every Passkey of the given User, newest create time first. When the User has no Passkey, it SHALL return an empty list, not an error.

#### Scenario: Two recorded passkeys

- **WHEN** the User has Passkeys created on 2026-10-01 and 2026-10-20
- **THEN** both are returned, the one created on 2026-10-20 first

#### Scenario: Nothing recorded

- **WHEN** the User has no Passkey
- **THEN** an empty list is returned
