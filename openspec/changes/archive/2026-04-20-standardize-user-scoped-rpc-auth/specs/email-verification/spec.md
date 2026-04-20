## MODIFIED Requirements

### Requirement: Resend verification email via RPC

The system SHALL provide an RPC method that allows authenticated users to resend the verification email for their own account. The backend SHALL proxy this request to Zitadel's `POST /v2/users/{userId}/email/resend` API.

The request SHALL carry an explicit `user_id` that the backend verifies against the JWT-derived userID; mismatches SHALL be rejected with `PERMISSION_DENIED` before any Zitadel call is made.

The infrastructure layer (`EmailVerifier.ResendVerification`) SHALL emit a structured INFO log entry on successful API call completion, and a structured ERROR log entry on failure. Both log entries MUST include the `external_id` field.

#### Scenario: User requests resend from Settings page

- **WHEN** an authenticated user calls the resend verification RPC
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the backend SHALL extract the user's `external_id` from JWT claims
- **AND** the backend SHALL call Zitadel's email resend API with the `external_id`
- **AND** Zitadel SHALL send a new verification email to the user

#### Scenario: Resend Zitadel API call succeeds

- **WHEN** `EmailVerifier.ResendVerification` is called and the Zitadel `ResendEmailCode` API call completes successfully
- **THEN** `EmailVerifier.ResendVerification` SHALL emit an INFO log entry with `msg="email verification resent"` and `external_id`

#### Scenario: Resend Zitadel API call fails

- **WHEN** `EmailVerifier.ResendVerification` is called and the Zitadel `ResendEmailCode` API call returns an error
- **THEN** `EmailVerifier.ResendVerification` SHALL emit an ERROR log entry with `msg="failed to resend email code"` and `external_id`
- **AND** the error SHALL be returned to the caller

#### Scenario: User is already verified

- **WHEN** an authenticated user whose email is already verified calls the resend verification RPC
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the backend SHALL return a `FailedPrecondition` error indicating the email is already verified

#### Scenario: Rapid resend attempts

- **WHEN** a user calls the resend verification RPC more than 3 times within 10 minutes
- **THEN** the backend SHALL return a `ResourceExhausted` error

#### Scenario: Unauthenticated request

- **WHEN** an unauthenticated request calls the resend verification RPC
- **THEN** the backend SHALL reject the request with an authentication error

#### Scenario: user_id does not match authenticated user

- **WHEN** the resend verification RPC is called with a `user_id` that differs from the userID derived from the JWT
- **THEN** the backend SHALL return `PERMISSION_DENIED`
- **AND** no Zitadel API call SHALL be made
- **AND** the `EmailVerifier.ResendVerification` infrastructure path SHALL NOT be invoked
