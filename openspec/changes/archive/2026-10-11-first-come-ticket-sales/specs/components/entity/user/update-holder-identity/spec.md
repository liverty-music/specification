# Spec Delta

## Purpose

Stores the 本人確認 (identity check) name and phone number a User checks out with, for the next checkout's prefill.

## ADDED Requirements

### Requirement: Identity replaced as a whole

UpdateHolderIdentity SHALL replace the User's holder full name and holder phone number with the given ones and return the updated User. It SHALL fail with InvalidArgument when either breaks the holder identity rules, and with NotFound when no User has the id.

#### Scenario: First checkout

- **WHEN** a User without a holder identity is updated with a name and a phone number
- **THEN** both are stored

#### Scenario: Invalid name

- **WHEN** the name is empty
- **THEN** UpdateHolderIdentity fails with InvalidArgument and nothing changes
