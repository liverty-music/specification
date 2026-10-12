# Spec Delta

## Purpose

Stores a User's full name and phone number, the 本人確認 (identity check) details shown on the face of the User's tickets.

## ADDED Requirements

### Requirement: Store the full name and phone number

UpdatePersonalDetails SHALL set the User's full name and phone number to the given values, leave the User's other attributes unchanged, and return the updated User. It SHALL fail with InvalidArgument when the values break the User's personal details rule and with NotFound when no User has the id. Repeating it with the same values SHALL succeed without a further change.

#### Scenario: First details
- **WHEN** a User without a full name is updated with 山田 花子 and `+819012345678`
- **THEN** the User has that full name and phone number

#### Scenario: Correction
- **WHEN** a User's phone number is changed while the User holds Issued Tickets
- **THEN** the User has the new phone number, and the Tickets' faces show it

#### Scenario: Invalid phone number
- **WHEN** the phone number is `090-1234-5678`
- **THEN** UpdatePersonalDetails fails with InvalidArgument and nothing changes

#### Scenario: Unknown user
- **WHEN** no User has the id
- **THEN** UpdatePersonalDetails fails with NotFound
