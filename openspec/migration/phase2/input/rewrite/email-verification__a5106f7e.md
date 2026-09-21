<!-- spec: email-verification | target: components/infrastructure/fan/api/zitadel/verification | flags: CLASSNAME | new_name: Trigger verification email on user creation -->

### Requirement: Trigger verification email on user creation

The system SHALL publish a `USER.created` event to NATS JetStream when a user is successfully provisioned in the backend. A consumer SHALL subscribe to this event and call Zitadel's `POST /v2/users/{externalId}/email/send` API to trigger a verification email via the configured SMTP provider (Postmark).

The infrastructure layer (`EmailVerifier.SendVerification`) SHALL emit a structured INFO log entry on successful API call completion. On failure, the error is returned to the caller without logging — the caller (`UserConsumer`) is responsible for logging the failure. The INFO log entry MUST include the `external_id` field.

#### Scenario: New user signs up via Passkey

- **WHEN** a new user completes Passkey registration and the backend provisions the user record
- **THEN** the backend SHALL publish a `USER.created` event to the `USER` NATS JetStream stream
- **AND** the consumer SHALL call Zitadel's email send API with the user's `external_id` (Zitadel user ID)
- **AND** Zitadel SHALL send a verification email to the user's registered email address via Postmark

#### Scenario: Zitadel API call succeeds

- **WHEN** the consumer calls Zitadel's `SendEmailCode` API and the call completes successfully
- **THEN** `EmailVerifier.SendVerification` SHALL emit an INFO log entry with `msg="email verification sent"` and `external_id`

#### Scenario: Zitadel API call fails

- **WHEN** the consumer calls Zitadel's `SendEmailCode` API and the call returns an error
- **THEN** `EmailVerifier.SendVerification` SHALL return the error to the caller without logging (the caller is responsible for logging)
- **AND** the error SHALL be returned to the caller (existing retry/poison queue behaviour is unchanged)

#### Scenario: Zitadel API call fails transiently

- **WHEN** the consumer calls Zitadel's email send API and receives a transient error (network timeout, 5xx)
- **THEN** the NATS JetStream consumer SHALL retry the message with backoff
- **AND** the user creation SHALL NOT be affected (already persisted)

#### Scenario: User email is already verified

- **WHEN** the consumer calls Zitadel's email send API for a user whose email is already verified
- **THEN** the consumer SHALL handle the response gracefully (log and acknowledge the message)

#### Scenario: Duplicate USER.created event

- **WHEN** the consumer receives a duplicate `USER.created` event (e.g., NATS redelivery after ack timeout)
- **THEN** the consumer SHALL call Zitadel's email send API
- **AND** the operation SHALL be idempotent (re-sending a verification email has no adverse side effects)
