# Spec Delta

## ADDED Requirements

### Requirement: Create refuses the identity of a removed User

Create SHALL fail with FailedPrecondition, storing and announcing nothing, when a User with the same provider user ID was removed (User.Delete), also when that removal completes while Create runs. The email of a removed User SHALL be free for another provider user ID.

#### Scenario: Identity of a removed User

- **WHEN** Create runs for the provider user ID of a removed User
- **THEN** Create fails with FailedPrecondition, no User is stored and nothing is announced

#### Scenario: Removal completing during Create

- **WHEN** Create runs for a User's provider user ID while that User is being removed
- **THEN** Create fails and no User with that provider user ID exists afterwards

#### Scenario: Same email with a new identity

- **WHEN** Create runs with a removed User's email and a provider user ID no removed User had
- **THEN** a new User is stored
