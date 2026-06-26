# sales-reminders Specification

## Purpose
TBD - created by archiving change add-sales-phase-timeline. Update Purpose after archive.
## Requirements
### Requirement: Multi-Stage Reminder Scan

The system SHALL run a scheduled job that scans sales phases for approaching milestones and emits reminders for each due stage. Because no delayed-message mechanism exists, reminders SHALL be produced by a periodic scan.

#### Scenario: Reminder stages

- **WHEN** the reminder scan evaluates a sales phase
- **THEN** it SHALL emit a reminder for each due stage among: application open (`apply_start_time`), 24 hours before close, 1 hour before close (`apply_end_time`), and lottery-result day (`lottery_result_time`)

#### Scenario: Scan cadence finer than tightest window

- **WHEN** the reminder job is scheduled
- **THEN** it SHALL run approximately every 15 minutes, which is shorter than the tightest reminder window (the 1-hour-before stage)

#### Scenario: Lottery-result reminder fires on the morning of the result day

- **WHEN** `lottery_result_time` denotes a result day without a precise time
- **THEN** the result-day reminder SHALL fire that morning (09:00 in the user's timezone)

#### Scenario: Milestones already past when a phase is first seen are not fired

- **WHEN** a phase is first persisted and one of its milestones is already in the past
- **THEN** the scan SHALL NOT retroactively fire that stage (the discovery announcement conveys current state); only milestones occurring after the phase becomes known SHALL fire

#### Scenario: Null milestone produces no reminder

- **WHEN** a sales phase has a null timestamp for a given stage
- **THEN** no reminder SHALL be emitted for that stage

#### Scenario: Payment deadline is not a reminder stage

- **WHEN** a sales phase has a non-null `payment_deadline_time`
- **THEN** the scan SHALL NOT emit a payment-deadline reminder in this capability
- **AND** payment reminders SHALL remain deferred until lottery win/loss gating exists, because only winners owe payment

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

### Requirement: Quiet Hours

The system SHALL avoid waking users at night for the time-based reminder scan. A reminder due during a user's quiet window (22:00–08:00 in the user's `time_zone`, falling back to `Asia/Tokyo` when `time_zone` is unset) SHALL be shifted rather than sent in the window. The shift SHALL never push a deadline-relative reminder past its deadline. (The event-driven discovery announcement is out of scope here — it fires from the daily daytime discovery job, not the scan, so it is not subject to this deferral.)

#### Scenario: Non-deadline reminder defers to morning

- **WHEN** a reminder whose stage is not deadline-relative (application open or lottery result) is due inside the quiet window
- **THEN** it SHALL be deferred to the window end (08:00 in the user's timezone)

#### Scenario: Deadline reminder shifts but never past the deadline

- **WHEN** a deadline-relative reminder (24h-before or 1h-before close) is due inside the quiet window
- **AND** the window end (08:00) is strictly before `apply_end_time`
- **THEN** it SHALL be deferred to 08:00
- **WHEN** instead `apply_end_time` is at or before the window end (i.e. falls within the quiet window or exactly at 08:00)
- **THEN** the scan SHALL look ahead and emit the reminder on its last run before the quiet window begins (a pre-quiet alert), since a periodic scan cannot send at a past time once the window has started
- **AND** it SHALL never wake the user during the window nor fire at/after the deadline

#### Scenario: Timezone fallback

- **WHEN** a user has no `time_zone` set
- **THEN** the quiet window SHALL be evaluated in `Asia/Tokyo`

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

