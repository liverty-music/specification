## MODIFIED Requirements

### Requirement: Every user call requires a signed-in caller

Every call to the user service except RequestPasskeyRecovery SHALL fail with Unauthenticated when the caller presents no valid sign-in token or the token names no identity, before the request is looked at further. RequestPasskeyRecovery SHALL be accepted without a sign-in token, because it serves people who cannot sign in.

#### Scenario: Not signed in

- **WHEN** a caller without a valid sign-in token calls any user service call other than RequestPasskeyRecovery
- **THEN** it fails with Unauthenticated and nothing is read or changed

#### Scenario: Recovery request without sign-in

- **WHEN** a caller without a sign-in token calls RequestPasskeyRecovery
- **THEN** the call is handled and does not fail with Unauthenticated

## ADDED Requirements

### Requirement: RequestPasskeyRecovery checks the address and hands it to the usecase

RequestPasskeyRecovery SHALL fail with InvalidArgument when the request carries no email address or one that is not a well-formed address of at most 165 characters. Otherwise it SHALL call UserUseCase.RequestPasskeyRecovery with the address and the client's network address, return its ResourceExhausted failure unchanged, and otherwise answer with the same empty success whatever the address. It SHALL use no sign-in identity even when the caller presents one.

#### Scenario: Well-formed address

- **WHEN** a caller requests recovery for `fan@example.com`
- **THEN** UserUseCase.RequestPasskeyRecovery runs for that address and the caller receives an empty success

#### Scenario: Malformed address

- **WHEN** a caller requests recovery for `not-an-address`
- **THEN** the call fails with InvalidArgument and nothing is announced

#### Scenario: Client over its limit

- **WHEN** UserUseCase.RequestPasskeyRecovery fails with ResourceExhausted
- **THEN** RequestPasskeyRecovery fails with ResourceExhausted
