# Spec Delta

## MODIFIED Requirements

### Requirement: A registered identity gets its existing user back

When User.Create fails with AlreadyExists, Create SHALL look the identity up with User.GetByProviderUserID. When a User is found, Create SHALL return that User unchanged: its email, name, home and preferred language are not overwritten by the new values. When no User has the provider user ID, the email belongs to another User and Create SHALL go on as "A user whose identity is gone is replaced" states. When the lookup fails for any other reason, Create SHALL fail with the lookup's error.

#### Scenario: Same identity again

- **WHEN** Create is called for an provider user ID that is already registered, with preferred language `en`, and the stored User's preferred language is `ja`
- **THEN** it returns the stored User, whose preferred language stays `ja`

#### Scenario: Email used by another identity

- **WHEN** Create is called with an email that a User with a different provider user ID already has, and that identity still exists
- **THEN** it fails with AlreadyExists and that User is unchanged

#### Scenario: Lookup after the conflict fails

- **WHEN** User.Create fails with AlreadyExists and the following User.GetByProviderUserID fails with Unavailable
- **THEN** Create fails with Unavailable

## ADDED Requirements

### Requirement: A user whose identity is gone is replaced

When the email belongs to another User, Create SHALL read that User with User.GetByEmail. When User.GetByEmail fails with NotFound, because the User was removed in the meantime, Create SHALL go on to store the new User. When the User read has the caller's provider user ID, because another call stored it in the meantime, Create SHALL return it. Otherwise Create SHALL ask User.HasIdentity about its provider user ID. When the identity exists, Create SHALL fail with AlreadyExists. When it does not, Create SHALL remove that User with UserUseCase.Delete and then store the new User with User.Create. A Delete that fails with NotFound means the User is already removed and Create SHALL go on. A Delete that fails with FailedPrecondition, because the User still has a deletion blocker, SHALL make Create fail with AlreadyExists, removing nothing. When the second User.Create fails with AlreadyExists, Create SHALL return the User that has the caller's provider user ID, and fail with AlreadyExists when there is none. Any other failure of User.GetByEmail, User.HasIdentity, UserUseCase.Delete or User.Create SHALL be returned with its own code. The new User SHALL receive nothing from the removed one.

#### Scenario: Account left behind by a deletion

- **WHEN** a User's identity was removed but the User remains, and Create is called with its email by a new identity
- **THEN** the old User is removed, a new User is stored and returned, and its orders and tickets stay with the removed User's id

#### Scenario: Left-behind account with a blocker

- **WHEN** the User whose identity is gone holds an Issued Ticket for an upcoming concert
- **THEN** Create fails with AlreadyExists and that User remains

#### Scenario: Identity cannot be checked

- **WHEN** User.HasIdentity fails with Unavailable
- **THEN** Create fails with Unavailable and nothing is removed

#### Scenario: Two sign-ups repair at once

- **WHEN** two calls of Create by the same new identity both find the old User, and the other call removes it and stores the new User first
- **THEN** the call returns the new User

#### Scenario: Old user removed before it is read

- **WHEN** User.GetByEmail fails with NotFound after the email conflict
- **THEN** Create stores the new User and returns it

#### Scenario: Already repaired before the read

- **WHEN** User.GetByEmail returns a User with the caller's provider user ID
- **THEN** Create returns that User and removes nothing
