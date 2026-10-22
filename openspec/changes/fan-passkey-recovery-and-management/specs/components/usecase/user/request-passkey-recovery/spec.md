## Purpose

UserUseCase.RequestPasskeyRecovery lets a person who cannot sign in ask for a passkey registration link by typing their email, without anyone learning from the answer, or from how long it takes, whether the address has an account.

## ADDED Requirements

### Requirement: A recovery request is announced for the matching User only

RequestPasskeyRecovery SHALL take an email address and SHALL succeed in the same way whether or not the address belongs to a User. After it has answered, it SHALL read the User with User.GetByEmail; when one is found it SHALL announce a passkey recovery request for that User, and when none is found it SHALL announce nothing. Neither the answer nor its timing SHALL depend on the read. A failure to read or to announce SHALL be logged and SHALL NOT fail the call.

#### Scenario: Address of a fan account

- **WHEN** RequestPasskeyRecovery runs for the email of a User
- **THEN** the call succeeds and a passkey recovery request is announced for that User

#### Scenario: Address with no account

- **WHEN** RequestPasskeyRecovery runs for an address no User has
- **THEN** the call succeeds exactly as for a User's address and nothing is announced

#### Scenario: Store unavailable

- **WHEN** User.GetByEmail fails with Unavailable
- **THEN** the call still succeeds and the failure is logged

### Requirement: Requests per address and per client are limited

RequestPasskeyRecovery SHALL announce at most 3 recovery requests per address, letter case ignored, in any 60 minutes; a further request for that address within the window SHALL succeed without announcing. Requests from one client SHALL be limited to 10 in any 60 minutes; a further request SHALL fail with ResourceExhausted and announce nothing.

#### Scenario: Fourth request for one address

- **WHEN** 3 requests were made for an address in the last 60 minutes and a fourth arrives
- **THEN** the call succeeds and nothing is announced

#### Scenario: Eleventh request from one client

- **WHEN** one client made 10 requests in the last 60 minutes and makes another
- **THEN** it fails with ResourceExhausted
