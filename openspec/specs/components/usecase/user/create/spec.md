# UserUseCase.Create

## Purpose

Registers the signed-in person as a User, or returns their existing User when their identity is already registered, optionally capturing their home area and preferred language at sign-up.

## Requirements

### Requirement: Input is checked before anything is stored

Create SHALL take a new User's external id, email, name and, optionally, a Home and a preferred language. It SHALL fail with InvalidArgument and store nothing when the Home is invalid or when a preferred language is given that is not valid, in the terms of the User entity.

#### Scenario: Invalid home

- **WHEN** Create is called with a Home whose level 1 `US-CA` does not belong to country code `JP`
- **THEN** it fails with InvalidArgument and no User is stored

#### Scenario: Malformed preferred language

- **WHEN** Create is called with preferred language `JA`
- **THEN** it fails with InvalidArgument and no User is stored

### Requirement: A new identity is registered

When no User exists for the external id or the email, Create SHALL call User.Create with the given values and return the stored User, with its Home when one was given and with the preferred language when one was given.

#### Scenario: New user with home and language

- **WHEN** Create is called for an unregistered identity with a Home `JP-13` and preferred language `ja`
- **THEN** it returns a new User carrying that Home and preferred language `ja`

#### Scenario: New user without optional values

- **WHEN** Create is called for an unregistered identity with no Home and no preferred language
- **THEN** it returns a new User with no home and no preferred language

### Requirement: A registered identity gets its existing user back

When User.Create fails with AlreadyExists, Create SHALL look the identity up with User.GetByExternalID. When a User is found, Create SHALL return that User unchanged: its email, name, home and preferred language are not overwritten by the new values. When no User has the external id, the email belongs to another identity and Create SHALL fail with AlreadyExists. When the lookup fails for any other reason, Create SHALL fail with the lookup's error.

#### Scenario: Same identity again

- **WHEN** Create is called for an external id that is already registered, with preferred language `en`, and the stored User's preferred language is `ja`
- **THEN** it returns the stored User, whose preferred language stays `ja`

#### Scenario: Email used by another identity

- **WHEN** Create is called with an email that a User with a different external id already has
- **THEN** it fails with AlreadyExists

#### Scenario: Lookup after the conflict fails

- **WHEN** User.Create fails with AlreadyExists and the following User.GetByExternalID fails with Unavailable
- **THEN** Create fails with Unavailable

### Requirement: A verification email follows every new user

When Create stores a new User, it SHALL announce the new User, and each announcement SHALL cause User.SendVerification to run for that User's external id; when Create returns an existing User, nothing is announced or sent. A failed send SHALL be retried up to 3 more times and then given up, and the User stays created. If announcing the new User fails, Create still succeeds and no verification email is sent for it. When email verification is not configured, the announcement is accepted and no email is sent.

#### Scenario: New user

- **WHEN** Create stores a new User
- **THEN** a verification email is sent to the User's address

#### Scenario: User already existed

- **WHEN** Create returns an already registered User
- **THEN** no verification email is sent

#### Scenario: Sending keeps failing

- **WHEN** sending the verification email fails on the first attempt and on 3 retries
- **THEN** the send is given up and the User stays created

#### Scenario: Announcing fails

- **WHEN** the new User is stored but announcing it fails
- **THEN** Create returns the new User and no verification email is sent

#### Scenario: Verification not configured

- **WHEN** a new User is announced while email verification is not configured
- **THEN** no email is sent and the User stays created
