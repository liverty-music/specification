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

## ADDED Requirements

### Requirement: VerifyEmail checks the link and hands it to the usecase

VerifyEmail SHALL fail with InvalidArgument when the request carries no User id or one that is not a UUID, or no code or one longer than 32 characters. Otherwise it SHALL call UserUseCase.VerifyEmail with the User id, the code and the client's network address, and return its outcome unchanged. It SHALL use no sign-in identity even when the caller presents one.

#### Scenario: Link from the email

- **WHEN** a caller calls VerifyEmail with a User id and a code
- **THEN** UserUseCase.VerifyEmail runs for them and its outcome is returned

#### Scenario: Malformed link

- **WHEN** a caller calls VerifyEmail with a User id that is not a UUID
- **THEN** the call fails with InvalidArgument and the usecase does not run
