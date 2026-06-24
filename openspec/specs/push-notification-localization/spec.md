# push-notification-localization Specification

## Purpose
TBD - created by archiving change localize-push-notification-text. Update Purpose after archive.
## Requirements
### Requirement: Localized Notification Copy

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

### Requirement: Concert Discovery Notification Content

The system SHALL localize the concert-discovery follower notification that is sent when new concerts are found for a followed artist. The `title` SHALL be the artist name (language-independent) and the `body` SHALL state the count of newly discovered concerts in the recipient's resolved language.

#### Scenario: Body in English

- **WHEN** newly discovered concerts are notified to a recipient resolved to `en`
- **THEN** the `body` SHALL read "1 new concert found" for a single concert
- **AND** the `body` SHALL read "N new concerts found" for N concerts where N is greater than one

#### Scenario: Body in Japanese

- **WHEN** newly discovered concerts are notified to a recipient resolved to `ja`
- **THEN** the `body` SHALL state the new-concert count in Japanese (e.g. "新しいライブが N 件見つかりました")

#### Scenario: Title and deep-link unaffected by language

- **WHEN** a concert-discovery notification is built for any recipient
- **THEN** the `title` SHALL be the artist name regardless of language
- **AND** the `url` SHALL deep-link to the artist's concerts and the `tag` SHALL deduplicate per artist, both regardless of language

