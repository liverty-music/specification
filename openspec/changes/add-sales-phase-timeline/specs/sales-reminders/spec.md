## ADDED Requirements

### Requirement: Multi-Stage Reminder Scan

The system SHALL run a scheduled job that scans sales phases for approaching milestones and emits reminders for each due stage. Because no delayed-message mechanism exists, reminders SHALL be produced by a periodic scan.

#### Scenario: Reminder stages

- **WHEN** the reminder scan evaluates a sales phase
- **THEN** it SHALL emit a reminder for each due stage among: application open (`apply_start_time`), 24 hours before close, 1 hour before close (`apply_end_time`), and lottery-result day (`lottery_result_time`)

#### Scenario: Scan cadence finer than tightest window

- **WHEN** the reminder job is scheduled
- **THEN** its scan interval SHALL be shorter than the tightest reminder window (the 1-hour-before stage)

#### Scenario: Null milestone produces no reminder

- **WHEN** a sales phase has a null timestamp for a given stage
- **THEN** no reminder SHALL be emitted for that stage

### Requirement: Reminder Audience

The system SHALL target reminders to the followers of the performing artists of the sales phase's series, applying the existing hype-level filtering used for new-concert notifications.

#### Scenario: Resolve audience from series

- **WHEN** a sales-phase reminder is due
- **THEN** the system SHALL resolve the series' events and their performing artists
- **AND** select followers of those artists according to their hype level
- **AND** deliver the reminder only to the selected followers' push subscriptions

### Requirement: Once-Only Delivery

The system SHALL guarantee that each reminder is delivered to a given user at most once, despite overlapping scans, by recording sent reminders keyed by the sales phase's stable id.

#### Scenario: Duplicate scan does not resend

- **WHEN** a user has already received a reminder for a given sales phase and stage
- **THEN** a subsequent scan SHALL NOT send that reminder again
- **AND** the sent record SHALL be keyed by `(user_id, sales_phase_id, stage)`, referencing the phase's surrogate id so that two phases of the same series differing only by `channel` are never conflated

### Requirement: Reminder Delivery Reuses Web Push

The system SHALL deliver reminders through the existing Web Push infrastructure rather than introducing a new delivery channel.

#### Scenario: Send via existing sender

- **WHEN** a reminder is delivered
- **THEN** it SHALL be sent via the existing Web Push sender to the user's stored push subscriptions
- **AND** an expired subscription SHALL be handled the same way as in existing notifications (removed on a gone response)
