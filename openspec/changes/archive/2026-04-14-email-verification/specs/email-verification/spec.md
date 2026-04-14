# Email Verification

## Purpose

Defines the email verification flow for users who register via Passkey. Covers triggering verification emails on user creation, resending verification, and displaying verification status in the UI.

## ADDED Requirements

### Requirement: Trigger verification email on user creation

The system SHALL publish a `USER.created` event to NATS JetStream when a user is successfully provisioned in the backend. A consumer SHALL subscribe to this event and call Zitadel's `POST /v2/users/{externalId}/email/send` API to trigger a verification email via the configured SMTP provider (Postmark).

#### Scenario: New user signs up via Passkey

- **WHEN** a new user completes Passkey registration and the backend provisions the user record
- **THEN** the backend SHALL publish a `USER.created` event to the `USER` NATS JetStream stream
- **AND** the consumer SHALL call Zitadel's email send API with the user's `external_id` (Zitadel user ID)
- **AND** Zitadel SHALL send a verification email to the user's registered email address via Postmark

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

### Requirement: NATS USER stream

The system SHALL define a `USER` JetStream stream capturing all `USER.*` subjects, following the existing stream pattern (CONCERT, VENUE, ARTIST).

#### Scenario: Stream configuration

- **WHEN** the backend starts and ensures JetStream streams
- **THEN** a `USER` stream SHALL exist with subjects `USER.*`
- **AND** retention SHALL be `LimitsPolicy` with 7-day max age
- **AND** storage SHALL be `FileStorage` with 2-minute deduplication window

### Requirement: Resend verification email via RPC

The system SHALL provide an RPC method that allows authenticated users to resend the verification email for their own account. The backend SHALL proxy this request to Zitadel's `POST /v2/users/{userId}/email/resend` API.

#### Scenario: User requests resend from Settings page

- **WHEN** an authenticated user calls the resend verification RPC
- **THEN** the backend SHALL extract the user's `external_id` from JWT claims
- **AND** the backend SHALL call Zitadel's email resend API with the `external_id`
- **AND** Zitadel SHALL send a new verification email to the user

#### Scenario: User is already verified

- **WHEN** an authenticated user whose email is already verified calls the resend verification RPC
- **THEN** the backend SHALL return a `FailedPrecondition` error indicating the email is already verified

#### Scenario: Rapid resend attempts

- **WHEN** a user calls the resend verification RPC more than 3 times within 10 minutes
- **THEN** the backend SHALL return a `ResourceExhausted` error

#### Scenario: Unauthenticated request

- **WHEN** an unauthenticated request calls the resend verification RPC
- **THEN** the backend SHALL reject the request with an authentication error

### Requirement: Verification status display on Settings page

The frontend Settings page SHALL display the user's email verification status and provide a resend button for unverified users.

#### Scenario: Unverified user views Settings

- **WHEN** an authenticated user with an unverified email visits the Settings page
- **THEN** the page SHALL display the user's email address
- **AND** the page SHALL show a "not verified" indicator
- **AND** a "Resend verification email" button SHALL be visible

#### Scenario: Verified user views Settings

- **WHEN** an authenticated user with a verified email visits the Settings page
- **THEN** the page SHALL display the user's email address
- **AND** the page SHALL show a "verified" indicator
- **AND** the resend button SHALL NOT be visible

#### Scenario: User clicks resend button

- **WHEN** an unverified user clicks the "Resend verification email" button
- **THEN** the frontend SHALL call the backend resend verification RPC
- **AND** the button SHALL show a success confirmation on completion
- **AND** the button SHALL be disabled temporarily to prevent rapid re-clicks

### Requirement: Verification flow uses Zitadel hosted UI

Email verification SHALL be handled entirely by Zitadel's hosted verification page. No custom verification UI is built. The verification email links to Zitadel's default verification URL.

#### Scenario: User clicks verification link in email

- **WHEN** a user clicks the verification link in the email
- **THEN** the user SHALL be directed to Zitadel's hosted verification page
- **AND** after entering the code, Zitadel SHALL mark the email as verified
- **AND** the user SHALL be redirected back to the application
