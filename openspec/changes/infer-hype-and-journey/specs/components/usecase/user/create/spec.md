## MODIFIED Requirements

### Requirement: A new identity is registered

When a Home is given and no User exists for the provider user ID or the email, Create SHALL call User.Create with the given values and return the stored User, with its Home and, when one was given, its preferred language. When no Home is given, Create SHALL look the identity up with User.GetByProviderUserID and return its User unchanged; when the identity has no User, Create SHALL fail with FailedPrecondition and store nothing, because a new User needs a home. When that lookup fails for another reason, Create SHALL fail with the lookup's error.

#### Scenario: New user with home and language

- **WHEN** Create is called for an unregistered identity with a Home `JP-13` and preferred language `ja`
- **THEN** it returns a new User carrying that Home and preferred language `ja`

#### Scenario: New user without optional values

- **WHEN** Create is called for an unregistered identity with a Home `JP-13` and no preferred language
- **THEN** it returns a new User with that Home and no preferred language

#### Scenario: New identity without a home

- **WHEN** Create is called for an unregistered identity with no Home
- **THEN** it fails with FailedPrecondition and no User is stored

#### Scenario: Registered identity without a home

- **WHEN** Create is called with no Home for an identity that already has a User
- **THEN** it returns that User unchanged
