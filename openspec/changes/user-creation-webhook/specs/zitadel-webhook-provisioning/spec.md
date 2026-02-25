## ADDED Requirements

### Requirement: Webhook Endpoint for Zitadel Events

The backend SHALL expose an HTTP POST endpoint at `/webhooks/zitadel` that receives Zitadel Actions v2 event payloads. The endpoint SHALL be separate from Connect-RPC services and use HMAC signature verification for authentication.

#### Scenario: Receive valid user.human.added event

- **WHEN** Zitadel sends a POST to `/webhooks/zitadel` with a valid `user.human.added` event payload and valid `ZITADEL-Signature` header
- **THEN** the system SHALL parse the event payload and extract user data (`aggregateID`, `email`, `displayName`, `preferredLanguage`)
- **AND** the system SHALL return HTTP 200

#### Scenario: Reject request with invalid signature

- **WHEN** a POST is received at `/webhooks/zitadel` with an invalid or missing `ZITADEL-Signature` header
- **THEN** the system SHALL return HTTP 401 Unauthorized
- **AND** the system SHALL NOT process the event payload

#### Scenario: Ignore non-user events

- **WHEN** Zitadel sends an event with `event_type` other than `user.human.added`
- **THEN** the system SHALL return HTTP 200 without processing

### Requirement: User UPSERT from Webhook

The system SHALL perform an UPSERT operation when processing a `user.human.added` webhook event. If the user does not exist (by `external_id`), a new record SHALL be created. If the user already exists, the record SHALL be updated with richer profile data from the webhook payload.

#### Scenario: Webhook arrives before Create RPC (new user)

- **WHEN** a `user.human.added` event is received for an `aggregateID` that does not exist in the `users` table
- **THEN** the system SHALL INSERT a new user record with `external_id` set to `aggregateID`, `email`, `name` set to `displayName`, and `preferred_language` set to `preferredLanguage`

#### Scenario: Webhook arrives after Create RPC (enrich existing user)

- **WHEN** a `user.human.added` event is received for an `aggregateID` that already exists in the `users` table
- **THEN** the system SHALL UPDATE the existing record, setting `name` and `preferred_language` only when the webhook provides non-empty values
- **AND** the system SHALL NOT overwrite existing non-empty values with empty strings

#### Scenario: Create RPC arrives after webhook (idempotent)

- **WHEN** the `Create` RPC is called for a user that was already created by the webhook
- **THEN** the system SHALL return `connect.CodeAlreadyExists` (existing behavior, unchanged)
- **AND** the frontend SHALL handle this as success (existing behavior, unchanged)

### Requirement: Webhook Signing Key Management

The Zitadel Target signing key SHALL be stored in GCP Secret Manager and synced to Kubernetes via External Secrets Operator, consistent with existing secret management patterns.

#### Scenario: Signing key available at startup

- **WHEN** the backend service starts
- **THEN** it SHALL read the Zitadel webhook signing key from environment configuration
- **AND** use it for HMAC signature verification of incoming webhook requests

#### Scenario: Signing key rotation

- **WHEN** the Zitadel Target is patched and a new signing key is generated
- **THEN** the new key SHALL be stored in GCP Secret Manager
- **AND** the External Secrets Operator SHALL sync the updated key to the Kubernetes Secret
- **AND** the backend SHALL pick up the new key on next restart or secret refresh
