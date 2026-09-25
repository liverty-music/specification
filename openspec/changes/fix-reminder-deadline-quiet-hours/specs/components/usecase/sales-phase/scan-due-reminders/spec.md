# Spec Delta

## MODIFIED Requirements

### Requirement: A stage is requested once its due time has passed

For each fan and each stage that applies to the phase, ScanDueReminders SHALL request a reminder once the stage's due time has passed, the stage has not expired, and SalesPhaseReminder.ListSentStages does not show that stage as sent to that fan. The due time of `APPLY_OPEN`, `APPLY_CLOSE_24H` and `APPLY_CLOSE_1H` SHALL be the stage's anchor; the due time of `RESULT_DAY` SHALL be 09:00 in the fan's time zone on the calendar day, in that time zone, of the lottery result time, whether or not the result time has a precise hour. A stage whose anchor is earlier than the phase's discovered time SHALL NOT be requested.

A stage expires as follows: `APPLY_CLOSE_24H` and `APPLY_CLOSE_1H` at the apply end time; `APPLY_OPEN` at the apply end time when it is known, otherwise it never expires; `RESULT_DAY` at the end of the calendar day, in the fan's time zone, of the lottery result time. A fan who starts tracking after a stage's due time but before it expires SHALL still be reminded of it on the next run while the phase is listed; a fan who starts tracking after a stage has expired SHALL NOT be reminded of it.

When the sent stages cannot be read, ScanDueReminders SHALL request the due reminders anyway and rely on DeliverReminder not to repeat a sent one. A request that cannot be queued SHALL be skipped and retried by a later run.

#### Scenario: Application opens

- **WHEN** a phase's apply start time has just passed and `APPLY_OPEN` was not sent to a tracking fan
- **THEN** an `APPLY_OPEN` reminder is requested for the fan

#### Scenario: Already sent

- **WHEN** `APPLY_OPEN` was already recorded as sent to the fan
- **THEN** no reminder is requested again

#### Scenario: Result day

- **WHEN** a phase's lottery result time is 15 July 18:00 and the fan's time zone is Asia/Tokyo
- **THEN** the `RESULT_DAY` reminder becomes due at 15 July 09:00 Asia/Tokyo

#### Scenario: Milestone already past when the phase was discovered

- **WHEN** a phase is discovered at 12:00 on the day its application opened at 10:00
- **THEN** no `APPLY_OPEN` reminder is ever requested for it

#### Scenario: Unknown milestone

- **WHEN** a phase has no apply end time
- **THEN** no `APPLY_CLOSE_24H` or `APPLY_CLOSE_1H` reminder is requested

#### Scenario: No payment reminder

- **WHEN** a phase has a payment deadline time
- **THEN** no reminder is requested for the payment deadline

#### Scenario: Application window closed before the open reminder was sent

- **WHEN** a fan starts tracking after a phase's apply end time and `APPLY_OPEN` was never sent to that fan
- **THEN** no `APPLY_OPEN` reminder is requested for that fan

#### Scenario: Result day has ended

- **WHEN** the current time is past the end of the lottery result day in the fan's time zone and `RESULT_DAY` was never sent to that fan
- **THEN** no `RESULT_DAY` reminder is requested for that fan

### Requirement: Quiet hours

ScanDueReminders SHALL NOT send a reminder in the fan's quiet window, 22:00 to 08:00 in the fan's time zone, falling back to Asia/Tokyo when the fan's time zone is unset or not recognised. A stage due inside the window SHALL be deferred as follows: `APPLY_OPEN` and `RESULT_DAY` to the next 08:00; `APPLY_CLOSE_24H` and `APPLY_CLOSE_1H` to the next 08:00 when that is strictly before the apply end time, and otherwise to 21:00 — one hour before the quiet window begins — on the last run before the window, so the reminder itself never lands inside quiet hours. When even 21:00 is not strictly before the apply end time, no moment remains outside quiet hours before the deadline, and the stage SHALL NOT be requested on that run. A close-stage reminder SHALL never be requested at or after the apply end time.

#### Scenario: Opening during the night

- **WHEN** a phase opens at 02:00 in the fan's time zone
- **THEN** its `APPLY_OPEN` reminder becomes due at 08:00 that morning

#### Scenario: Close with the morning still before the deadline

- **WHEN** the `APPLY_CLOSE_24H` anchor is 23:00 and the apply end time is 23:00 the next day
- **THEN** the reminder becomes due at 08:00 the next morning

#### Scenario: Close before the morning

- **WHEN** the apply end time is 02:00, so the `APPLY_CLOSE_1H` anchor is 01:00
- **THEN** the reminder is requested on the last run before 21:00 the evening before

#### Scenario: Close already passed

- **WHEN** a fan starts tracking after a phase's apply end time
- **THEN** no `APPLY_CLOSE_24H` or `APPLY_CLOSE_1H` reminder is requested for that fan

#### Scenario: Time zone fallback

- **WHEN** a fan's time zone is unset or not a recognised time zone
- **THEN** the quiet window and due times are evaluated in Asia/Tokyo
