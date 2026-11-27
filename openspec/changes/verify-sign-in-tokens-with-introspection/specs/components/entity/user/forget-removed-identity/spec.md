# Spec Delta

## Purpose

Removes the record that a User's identity was removed, once that identity can no longer be used to sign in.

## ADDED Requirements

### Requirement: ForgetRemovedIdentity removes the record

ForgetRemovedIdentity SHALL remove the record of the removed provider user ID, after which User.Create no longer refuses it. A provider user ID with no record SHALL count as forgotten. It SHALL fail with InvalidArgument when the provider user ID is empty, and with Unavailable when the store cannot be reached.

#### Scenario: Recorded identity

- **WHEN** ForgetRemovedIdentity runs for a recorded provider user ID
- **THEN** no record of it remains

#### Scenario: No record

- **WHEN** ForgetRemovedIdentity runs for a provider user ID with no record
- **THEN** it succeeds

#### Scenario: Empty provider user ID

- **WHEN** the provider user ID is empty
- **THEN** it fails with InvalidArgument

#### Scenario: Store unreachable

- **WHEN** the store cannot be reached
- **THEN** it fails with Unavailable
