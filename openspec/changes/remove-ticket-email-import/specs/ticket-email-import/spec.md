## REMOVED Requirements

### Requirement: TicketEmail Entity
**Reason**: The ticket-email-import feature is retired. It depended on the OS/Gmail share sheet targeting the PWA, which no longer offers a share action that can reach the app, so the ingestion path is permanently non-functional.
**Migration**: None. No production traffic reached this feature (the parser was never wired and the frontend served an unavailable state). The `ticket_emails` table is dropped. Ticket status is tracked via the retained `ticket-journey` capability's manual `SetStatus`.

The system SHALL define a `TicketEmail` entity representing a parsed ticket-related email imported by a user. Each email is uniquely identified by an auto-generated ID and linked to a user and one or more events.

#### Scenario: TicketEmail data model

- **WHEN** a ticket email is represented
- **THEN** it SHALL include `id` (TicketEmailId, UUIDv7), `user_id` (UserId), `event_id` (EventId), `email_type` (TicketEmailType), and `raw_body` (string)
- **AND** it SHALL include nullable fields: `payment_deadline` (Timestamp), `lottery_start` (Timestamp), `lottery_end` (Timestamp), `application_url` (string)
- **AND** it SHALL include `parsed_data` (JSON-structured parse result from Gemini)

#### Scenario: TicketEmailType enum values

- **WHEN** a ticket email type is represented
- **THEN** it SHALL be one of: `LOTTERY_INFO` (lottery announcement with dates/URL), `LOTTERY_RESULT` (win/loss notification)
- **AND** `UNSPECIFIED` (value 0) SHALL exist as the default proto value but SHALL NOT be accepted in API requests

### Requirement: TicketEmail ID
**Reason**: Retired together with the `TicketEmail` entity.
**Migration**: None. The vacated proto message and its field numbers are reserved.

The system SHALL define a `TicketEmailId` wrapper message with UUID string validation, following the existing type-safe ID pattern.

#### Scenario: TicketEmailId validation

- **WHEN** a `TicketEmailId` is provided
- **THEN** it SHALL contain a `value` field of type `string`
- **AND** it SHALL be validated as a valid UUID format

### Requirement: Create Ticket Email
**Reason**: The `CreateTicketEmail` RPC has no reachable entry point after the share-target ingestion path was removed, and the Gemini parser is intentionally unwired.
**Migration**: None. The `TicketEmailService` RPC is removed and its numbers reserved for breaking-change review.

The system SHALL allow an authenticated user to create a ticket email record by submitting email text for parsing. The system persists the raw email, invokes Gemini Flash to parse it, and stores the structured result.

#### Scenario: Create with lottery info email

- **WHEN** an authenticated user calls `CreateTicketEmail` with `raw_body`, `email_type` = `LOTTERY_INFO`, and one or more `event_ids`
- **THEN** the system SHALL parse the email body using Gemini Flash
- **AND** the system SHALL extract `lottery_start`, `lottery_end`, and `application_url` if present
- **AND** the system SHALL persist one `TicketEmail` record per `event_id`
- **AND** the system SHALL return the created records with parsed data

#### Scenario: Create with lottery result email

- **WHEN** an authenticated user calls `CreateTicketEmail` with `raw_body`, `email_type` = `LOTTERY_RESULT`, and one or more `event_ids`
- **THEN** the system SHALL parse the email body using Gemini Flash
- **AND** the system SHALL extract win/loss status, `payment_deadline` (if applicable), and payment status (paid/unpaid)
- **AND** the system SHALL persist one `TicketEmail` record per `event_id`
- **AND** the system SHALL return the created records with parsed data

#### Scenario: Gemini parse failure

- **WHEN** the Gemini Flash API call fails or returns unparseable results
- **THEN** the system SHALL return an `INTERNAL` error
- **AND** the system SHALL NOT persist any `TicketEmail` records

#### Scenario: User identity from auth context

- **WHEN** `CreateTicketEmail` is called
- **THEN** the `user_id` SHALL be derived from the authentication context, not from the request body

### Requirement: Update Ticket Email
**Reason**: The `UpdateTicketEmail` RPC is unreachable once the create/import flow is removed.
**Migration**: None. Ticket journey status is set only via the retained `ticket-journey` capability's manual `SetStatus`.

The system SHALL allow an authenticated user to update a previously created ticket email record with corrections, and trigger `TicketJourney` status updates based on the confirmed data.

#### Scenario: Confirm and update lottery info

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id` and corrected fields
- **AND** the email type is `LOTTERY_INFO`
- **THEN** the system SHALL update the `TicketEmail` record with the corrected values
- **AND** the system SHALL set `TicketJourney` status to `TRACKING` for each associated event

#### Scenario: Confirm lottery win with unpaid status

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id`
- **AND** the confirmed data indicates lottery win with payment pending
- **THEN** the system SHALL update the `TicketEmail` record
- **AND** the system SHALL set `TicketJourney` status to `UNPAID` for each associated event

#### Scenario: Confirm lottery win with paid status

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id`
- **AND** the confirmed data indicates lottery win with payment already completed (e.g., credit card auto-charge)
- **THEN** the system SHALL update the `TicketEmail` record
- **AND** the system SHALL set `TicketJourney` status to `PAID` for each associated event

#### Scenario: Confirm lottery loss

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id`
- **AND** the confirmed data indicates lottery loss
- **THEN** the system SHALL update the `TicketEmail` record
- **AND** the system SHALL set `TicketJourney` status to `LOST` for each associated event

#### Scenario: Update non-existent ticket email

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id` that does not exist
- **THEN** the system SHALL return a `NOT_FOUND` error

#### Scenario: Update another user's ticket email

- **WHEN** an authenticated user calls `UpdateTicketEmail` with a `ticket_email_id` owned by a different user
- **THEN** the system SHALL return a `NOT_FOUND` error (no information leak)

### Requirement: TicketEmail Database Schema
**Reason**: The `ticket_emails` table has no remaining reader or writer once the use case and repository are removed.
**Migration**: `DROP TABLE ticket_emails`. No other table holds an inbound foreign key to it; `ticket_journeys` is unaffected.

The system SHALL store ticket emails in a `ticket_emails` table.

#### Scenario: Table structure

- **WHEN** the `ticket_emails` table is created
- **THEN** it SHALL have columns: `id` (UUID PK), `user_id` (UUID FK → users), `event_id` (UUID FK → events), `email_type` (SMALLINT), `raw_body` (TEXT), `parsed_data` (JSONB), `payment_deadline` (TIMESTAMPTZ nullable), `lottery_start` (TIMESTAMPTZ nullable), `lottery_end` (TIMESTAMPTZ nullable), `application_url` (TEXT nullable)
- **AND** it SHALL have an index on `(user_id, event_id)` for efficient lookups

### Requirement: PWA Share Target
**Reason**: Already dormant; the removal makes the retirement complete. The OS/Gmail share action that fed this path no longer exists.
**Migration**: None. The `share_target` declaration and the disabled Service Worker interception comment are removed.

The frontend PWA SHALL NOT register as a share target. The Android Gmail app no longer offers a share action that can target the PWA, so the share-target ingestion path is non-functional and SHALL be removed to avoid presenting a broken entry point.

#### Scenario: Manifest has no share_target

- **WHEN** the PWA manifest is configured
- **THEN** it SHALL NOT include a `share_target` entry

#### Scenario: Service Worker does not intercept share POST

- **WHEN** the Service Worker is configured
- **THEN** it SHALL NOT register a handler that intercepts share-target POST requests

### Requirement: Email Import Wizard
**Reason**: The wizard is no longer retained for a future revival; the capability is being removed outright.
**Migration**: None. The wizard route, its RPC client, DI/route registration, and build-template marker are deleted.

The frontend SHALL retain the email import wizard code but make it unavailable to users. The wizard route SHALL NOT be reachable from navigation and SHALL present an unavailable state if accessed directly, until the email-import ingestion path is revived.

#### Scenario: Import entry is unavailable

- **WHEN** a user browses the application
- **THEN** there SHALL be no navigation entry leading to the email import wizard

#### Scenario: Direct access shows unavailable state

- **WHEN** a user navigates directly to the import wizard route
- **THEN** the application SHALL present an unavailable state rather than the functional wizard

#### Scenario: Wizard code is retained

- **WHEN** the email-import feature is later revived
- **THEN** the wizard components and RPC client SHALL still exist to be re-enabled without re-implementation
