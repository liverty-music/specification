# Notify

## Purpose

TBD - created by archiving change introduce-notification-service. Update Purpose after archive.

## Requirements

### Requirement: Notify records the delivery outcome
The service SHALL record the delivery outcome of each notification's channel send: `queued` on creation, then `delivered` once the channel accepts the send, or `failed` (with a failure reason) on error, so that "did this notification reach the user?" is answerable from stored state. (Web push provides no separate sent-vs-delivered receipt, so `delivered` denotes acceptance by the push service; a distinct `sent` state is not modelled for this channel.)

In addition to persisting the outcome, a `failed` delivery SHALL be surfaced as an operational signal — logged at WARNING with the failure reason, and emitted as a delivery-outcome metric labelled by outcome and failure reason — so that a systemic delivery failure is observable without querying the database. A `failed` outcome SHALL NOT be observable only from stored state.

#### Scenario: Successful web-push send is recorded as delivered
- **WHEN** the web-push channel send for a notification succeeds
- **THEN** the notification's delivery status SHALL be recorded as `delivered` with a delivery timestamp

#### Scenario: Failed send is recorded as failed, not dropped
- **WHEN** the web-push channel send fails (e.g. the push service rejects it)
- **THEN** the notification's delivery status SHALL be recorded as `failed` with a failure reason
- **AND** the notification record SHALL remain so the failure is auditable and the send is re-dispatchable

#### Scenario: Failed send is surfaced as an operational signal
- **WHEN** a notification's delivery is recorded as `failed`
- **THEN** the service SHALL log the failure at WARNING including the failure reason
- **AND** SHALL emit a delivery-outcome metric labelled by outcome and failure reason
- **AND** the failure SHALL therefore be detectable without reading the notifications table

### Requirement: Select push notification copy by recipient's preferred language

The system SHALL select the user-facing copy of every Web Push notification by the recipient's `preferred_language`, defaulting to `en` when the recipient has no language set. Localization SHALL reuse the existing `NotificationPayload` shape (`title`, `body`, `url`, `tag`); only the human-readable `title` and `body` are language-dependent, while `url` and `tag` remain language-independent.

#### Scenario: Recipient has a preferred language

- **WHEN** a Web Push notification is built for a recipient whose `preferred_language` is a supported code (e.g. `ja`)
- **THEN** the notification `title` and `body` SHALL be rendered in that language

#### Scenario: Recipient has no preferred language

- **WHEN** a Web Push notification is built for a recipient whose `preferred_language` is unset or empty
- **THEN** the notification `title` and `body` SHALL be rendered in `en`

#### Scenario: Recipient has an unsupported preferred language

- **WHEN** a Web Push notification is built for a recipient whose `preferred_language` is a code with no localized copy available
- **THEN** the notification `title` and `body` SHALL fall back to `en`

#### Scenario: Mixed-language audience for one notification event

- **WHEN** a single notification event fans out to recipients with differing `preferred_language` values
- **THEN** each recipient SHALL receive copy in their own resolved language
- **AND** the system SHALL build at most one payload per distinct resolved language rather than one per recipient subscription
