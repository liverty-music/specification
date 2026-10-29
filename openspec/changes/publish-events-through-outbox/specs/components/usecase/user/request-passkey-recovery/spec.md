## RENAMED Requirements

- FROM: `### Requirement: A recovery request is announced for the matching User only`
- TO: `### Requirement: A recovery link is started for the matching User only`

## MODIFIED Requirements

### Requirement: A recovery link is started for the matching User only

RequestPasskeyRecovery SHALL take an email address and SHALL succeed in the same way whether or not the address belongs to a User. After it has answered, it SHALL read the User with User.GetByEmail; when one is found it SHALL start UserUseCase.SendPasskeyRecoveryLink for that User, and when none is found it SHALL start nothing. The business key of the started work SHALL be the request itself: each request within the limits starts one SendPasskeyRecoveryLink. Neither the answer nor its timing SHALL depend on the read. A failure to read or to start SHALL be logged and SHALL NOT fail the call.

#### Scenario: Address of a fan account

- **WHEN** RequestPasskeyRecovery runs for the email of a User
- **THEN** the call succeeds and SendPasskeyRecoveryLink is started for that User

#### Scenario: Address with no account

- **WHEN** RequestPasskeyRecovery runs for an address no User has
- **THEN** the call succeeds exactly as for a User's address and nothing is started

#### Scenario: Store unavailable

- **WHEN** User.GetByEmail fails with Unavailable
- **THEN** the call still succeeds and the failure is logged

#### Scenario: Work cannot be started

- **WHEN** SendPasskeyRecoveryLink cannot be started for the User
- **THEN** the call still succeeds, the failure is logged and no link is sent

### Requirement: Requests per address and per client are limited

RequestPasskeyRecovery SHALL start at most 3 SendPasskeyRecoveryLink runs per address, letter case ignored, in any 60 minutes; a further request for that address within the window SHALL succeed without starting anything. Requests from one client SHALL be limited to 10 in any 60 minutes; a further request SHALL fail with ResourceExhausted and start nothing.

#### Scenario: Fourth request for one address

- **WHEN** 3 requests were made for an address in the last 60 minutes and a fourth arrives
- **THEN** the call succeeds and nothing is started

#### Scenario: Eleventh request from one client

- **WHEN** one client made 10 requests in the last 60 minutes and makes another
- **THEN** it fails with ResourceExhausted
