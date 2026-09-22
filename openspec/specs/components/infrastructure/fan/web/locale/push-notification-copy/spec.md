# Push Notification Copy

## Purpose

TBD - created by archiving change localize-push-notification-text. Update Purpose after archive.

## Requirements

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
