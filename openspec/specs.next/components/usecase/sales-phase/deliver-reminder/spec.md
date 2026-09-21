# Deliver Reminder

## Purpose

TBD - created by archiving change add-sales-phase-timeline. Update Purpose after archive.

## Requirements

### Requirement: Notification Content

The system SHALL build each notification (the discovery announcement and every reminder stage) per recipient, formatting times in the recipient's `time_zone` and selecting copy by the recipient's `preferred_language` (default `en`), reusing the existing `NotificationPayload` (`title`, `body`, `url`, `tag`).

#### Scenario: Payload fields per stage

- **WHEN** a notification is built for a phase and stage
- **THEN** `title` and `body` SHALL identify the artist, the tour (series) title, and the sales channel, and state the relevant time for that stage in the recipient's timezone
- **AND** when `channel` is `UNSPECIFIED` the copy SHALL use a generic ticket label
- **AND** `url` SHALL deep-link to the phase's application URL when present, else the series detail (a sales phase is series-level and has no single covered concert to fall back to)
- **AND** `tag` SHALL be unique per `(sales_phase_id, stage)` to deduplicate on the browser side

### Requirement: Reminder Delivery Reuses Web Push

The system SHALL deliver reminders through the existing Web Push infrastructure rather than introducing a new delivery channel.

#### Scenario: Send via existing sender

- **WHEN** a reminder is delivered
- **THEN** it SHALL be sent via the existing Web Push sender to the user's stored push subscriptions
- **AND** an expired subscription SHALL be handled the same way as in existing notifications (removed on a gone response)
