## ADDED Requirements

### Requirement: A new identity is registered with its language

When no User exists for the provider user ID or the email, Create SHALL call User.Create with the given values and return the stored User, with its preferred language and with its Home when one was given.

#### Scenario: New user with home and language

- **WHEN** Create is called for an unregistered identity with a Home `JP-13` and preferred language `ja`
- **THEN** it returns a new User carrying that Home and preferred language `ja`

#### Scenario: New user without a home

- **WHEN** Create is called for an unregistered identity with no Home and preferred language `en`
- **THEN** it returns a new User with no home and preferred language `en`

## MODIFIED Requirements

### Requirement: Input is checked before anything is stored

Create SHALL take a new User's provider user ID, email, name and preferred language and, optionally, a Home. It SHALL fail with InvalidArgument and store nothing when the Home is invalid or when the preferred language is missing or not valid, in the terms of the User entity.

#### Scenario: Invalid home

- **WHEN** Create is called with a Home whose level 1 `US-CA` does not belong to country code `JP`
- **THEN** it fails with InvalidArgument and no User is stored

#### Scenario: Malformed preferred language

- **WHEN** Create is called with preferred language `JA`
- **THEN** it fails with InvalidArgument and no User is stored

#### Scenario: Missing preferred language

- **WHEN** Create is called without a preferred language
- **THEN** it fails with InvalidArgument and no User is stored

## REMOVED Requirements

### Requirement: A new identity is registered
**Reason**: Replaced by "A new identity is registered with its language", which states the behavior without the scenarios of the removed behavior.
**Migration**: None.
