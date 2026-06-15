## MODIFIED Requirements

### Requirement: Reminder Audience

The system SHALL target reminders to the users who have a `Tracking` ticket journey on any event of the sales phase's series. A `Tracking` journey is an explicit "notify me about this sale" signal, so reminders no longer resolve audience from covered-event performers, follower lists, or hype-level proximity. Because a phase is series-level, audience is resolved series-wide: any tracked event in the series qualifies the user.

#### Scenario: Resolve audience from tracking journeys

- **WHEN** a sales-phase reminder is due
- **THEN** the system SHALL resolve the phase's `series_id` and find the users who have a `Tracking` ticket journey on any event of that series
- **AND** deliver the reminder only to those users' push subscriptions
- **AND** it SHALL NOT resolve audience from covered events, follower lists, or hype-level filtering

#### Scenario: Non-tracking fans are not targeted

- **WHEN** a fan follows the artist but has no `Tracking` ticket journey on any event of the series
- **THEN** that fan SHALL NOT receive the sales-phase reminder

### Requirement: Once-Only Delivery

The system SHALL guarantee that each reminder is delivered to a given user at most once, despite overlapping scans, by recording sent reminders keyed by the sales phase's surrogate id.

#### Scenario: Duplicate scan does not resend

- **WHEN** a user has already received a reminder for a given sales phase and stage
- **THEN** a subsequent scan SHALL NOT send that reminder again
- **AND** the sent record SHALL be keyed by `(user_id, sales_phase_id, stage)`, referencing the phase's surrogate id — which is stable because re-discovery converges in place on the `(series_id, apply_start_time)` match

### Requirement: Notification Content

The system SHALL build each notification (the discovery announcement and every reminder stage) per recipient, formatting times in the recipient's `time_zone` and selecting copy by the recipient's `preferred_language` (default `en`), reusing the existing `NotificationPayload` (`title`, `body`, `url`, `tag`).

#### Scenario: Payload fields per stage

- **WHEN** a notification is built for a phase and stage
- **THEN** `title` and `body` SHALL identify the artist, the tour (series) title, and the sales channel, and state the relevant time for that stage in the recipient's timezone
- **AND** when `channel` is `UNSPECIFIED` the copy SHALL use a generic ticket label
- **AND** `url` SHALL deep-link to the phase's application URL when present, else the series detail (a sales phase is series-level and has no single covered concert to fall back to)
- **AND** `tag` SHALL be unique per `(sales_phase_id, stage)` to deduplicate on the browser side
