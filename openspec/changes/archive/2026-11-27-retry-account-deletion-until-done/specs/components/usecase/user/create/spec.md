# Spec Delta

## MODIFIED Requirements

### Requirement: A new identity is registered with its language

When no User exists for the provider user ID or the email, Create SHALL call User.Create with the given values and return the stored User, with its preferred language and with its Home when one was given. When User.Create fails with FailedPrecondition, because the identity belongs to a removed User, Create SHALL fail with FailedPrecondition and no User is stored.

#### Scenario: New user with home and language

- **WHEN** Create is called for an unregistered identity with a Home `JP-13` and preferred language `ja`
- **THEN** it returns a new User carrying that Home and preferred language `ja`

#### Scenario: New user without a home

- **WHEN** Create is called for an unregistered identity with no Home and preferred language `en`
- **THEN** it returns a new User with no home and preferred language `en`

#### Scenario: Identity of a removed User

- **WHEN** Create is called for the identity of a removed User
- **THEN** it fails with FailedPrecondition and no User is stored
