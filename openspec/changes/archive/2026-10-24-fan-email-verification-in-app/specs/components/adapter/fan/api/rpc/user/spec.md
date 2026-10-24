## MODIFIED Requirements

### Requirement: Every user call requires a signed-in caller

Every call to the user service except RequestPasskeyRecovery and VerifyEmail SHALL fail with Unauthenticated when the caller presents no valid sign-in token or the token names no identity, before the request is looked at further. RequestPasskeyRecovery and VerifyEmail SHALL be accepted without a sign-in token, because they serve people who cannot or need not sign in.

#### Scenario: Not signed in

- **WHEN** a caller without a valid sign-in token calls any user service call other than RequestPasskeyRecovery and VerifyEmail
- **THEN** it fails with Unauthenticated and nothing is read or changed

#### Scenario: Recovery request without sign-in

- **WHEN** a caller without a sign-in token calls RequestPasskeyRecovery
- **THEN** the call is handled and does not fail with Unauthenticated

#### Scenario: Email verification without sign-in

- **WHEN** a caller without a sign-in token calls VerifyEmail
- **THEN** the call is handled and does not fail with Unauthenticated

### Requirement: RequestPasskeyRecovery checks the address and hands it to the usecase

RequestPasskeyRecovery SHALL fail with InvalidArgument when the request carries no email address or one that is not a well-formed address of at most 165 characters. Otherwise it SHALL call UserUseCase.RequestPasskeyRecovery with the address and answer with the same empty success whatever the address. Requests are limited per client, identified by its network address, before the call: a client that made 10 requests in the last 60 minutes SHALL be refused with ResourceExhausted without the usecase running. It SHALL use no sign-in identity even when the caller presents one.

#### Scenario: Well-formed address

- **WHEN** a caller requests recovery for `fan@example.com`
- **THEN** UserUseCase.RequestPasskeyRecovery runs for that address and the caller receives an empty success

#### Scenario: Malformed address

- **WHEN** a caller requests recovery for `not-an-address`
- **THEN** the call fails with InvalidArgument and nothing is announced

#### Scenario: Client over its limit

- **WHEN** a client that made 10 requests in the last 60 minutes requests recovery again
- **THEN** RequestPasskeyRecovery fails with ResourceExhausted and UserUseCase.RequestPasskeyRecovery does not run

## ADDED Requirements

### Requirement: VerifyEmail checks the link and hands it to the usecase

VerifyEmail SHALL fail with InvalidArgument when the request carries no User id or one that is not a UUID, or no code or one longer than 32 characters. Otherwise it SHALL call UserUseCase.VerifyEmail with the User id and the code, and return its outcome unchanged. Attempts are limited per client, identified by its network address, before the call: a client that made 10 attempts in the last 60 minutes SHALL be refused with ResourceExhausted without the usecase running. It SHALL use no sign-in identity even when the caller presents one.

#### Scenario: Link from the email

- **WHEN** a caller calls VerifyEmail with a User id and a code
- **THEN** UserUseCase.VerifyEmail runs for them and its outcome is returned

#### Scenario: Malformed link

- **WHEN** a caller calls VerifyEmail with a User id that is not a UUID
- **THEN** the call fails with InvalidArgument and the usecase does not run
