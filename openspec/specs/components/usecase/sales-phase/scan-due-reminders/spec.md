# Scan Due Reminders

## Purpose

ScanDueReminders runs every 15 minutes. For each sales phase with a pending milestone, it works out which reminder stages have become due for each fan tracking that phase's series, and requests one reminder for each fan, phase and stage not yet sent, with due times adjusted to the fan's time zone and quiet hours. It returns the number of reminders requested.

## Requirements

### Requirement: Runs every 15 minutes over phases with a pending milestone

ScanDueReminders SHALL run every 15 minutes, which is shorter than the tightest reminder stage (1 hour before close). Each run SHALL evaluate the phases returned by SalesPhase.ListPhasesWithPendingMilestones with a lookahead of 7 days and a lookback of 2 hours, and SHALL return the number of reminders it requested. When listing the phases fails, the run SHALL fail; when evaluating one phase fails, that phase SHALL be skipped and the others evaluated.

#### Scenario: Scan cadence

- **WHEN** 15 minutes have passed since the last run
- **THEN** ScanDueReminders runs again

#### Scenario: Phase opening in 3 days

- **WHEN** a phase opens in 3 days
- **THEN** the phase is evaluated on every run from now on

#### Scenario: One phase fails

- **WHEN** the audience of one phase cannot be read
- **THEN** that phase is skipped and the other phases are evaluated

### Requirement: The audience is the fans tracking the series

For each phase ScanDueReminders SHALL consider the fans returned by TicketJourney.ListUserIDsTrackingSeries for the phase's series, that is, the fans whose journey on an event of the series is still Tracking. A fan who follows the artist without tracking, or whose journey on the series has moved to Applied or later, SHALL NOT be reminded. A fan whose profile cannot be read SHALL be skipped.

#### Scenario: Tracking fan

- **WHEN** a fan tracks one event of the phase's series and a stage is due
- **THEN** a reminder is requested for that fan

#### Scenario: Follower who does not track

- **WHEN** a fan follows the artist but tracks no event of the series
- **THEN** no reminder is requested for that fan

#### Scenario: Fan who has applied

- **WHEN** a fan's only journey on the series is Applied and the result day arrives
- **THEN** no `RESULT_DAY` reminder is requested for that fan

### Requirement: A stage is requested once its due time has passed

For each fan and each stage that applies to the phase, ScanDueReminders SHALL request a reminder once the stage's due time has passed and SalesPhaseReminder.ListSentStages does not show that stage as sent to that fan. The due time of `APPLY_OPEN`, `APPLY_CLOSE_24H` and `APPLY_CLOSE_1H` SHALL be the stage's anchor; the due time of `RESULT_DAY` SHALL be 09:00 in the fan's time zone on the calendar day, in that time zone, of the lottery result time, whether or not the result time has a precise hour. A stage whose anchor is earlier than the phase's discovered time SHALL NOT be requested. A fan who starts tracking after a stage's due time SHALL still be reminded of it on the next run while the phase is listed. When the sent stages cannot be read, ScanDueReminders SHALL request the due reminders anyway and rely on DeliverReminder not to repeat a sent one. A request that cannot be queued SHALL be skipped and retried by a later run.

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

### Requirement: Quiet hours

ScanDueReminders SHALL NOT send a reminder in the fan's quiet window, 22:00 to 08:00 in the fan's time zone, falling back to Asia/Tokyo when the fan's time zone is unset or not recognised. A stage due inside the window SHALL be deferred as follows: `APPLY_OPEN` and `RESULT_DAY` to the next 08:00; `APPLY_CLOSE_24H` and `APPLY_CLOSE_1H` to the next 08:00 when that is strictly before the apply end time, and otherwise to the last run before the window begins. A close-stage reminder SHALL never be requested at or after the apply end time.

Known defect: liverty-music/backend#472

#### Scenario: Opening during the night

- **WHEN** a phase opens at 02:00 in the fan's time zone
- **THEN** its `APPLY_OPEN` reminder becomes due at 08:00 that morning

#### Scenario: Close with the morning still before the deadline

- **WHEN** the `APPLY_CLOSE_24H` anchor is 23:00 and the apply end time is 23:00 the next day
- **THEN** the reminder becomes due at 08:00 the next morning

#### Scenario: Close before the morning

- **WHEN** the apply end time is 02:00, so the `APPLY_CLOSE_1H` anchor is 01:00
- **THEN** the reminder is requested on the last run before 22:00 the evening before

#### Scenario: Close already passed

- **WHEN** a fan starts tracking after a phase's apply end time
- **THEN** no `APPLY_CLOSE_24H` or `APPLY_CLOSE_1H` reminder is requested for that fan

#### Scenario: Time zone fallback

- **WHEN** a fan's time zone is unset or not a recognised time zone
- **THEN** the quiet window and due times are evaluated in Asia/Tokyo

### Requirement: Reminder content

Each requested reminder SHALL carry a title that names the stage, a text that names the sales channel and the stage's milestone time, a link and a grouping tag, in the fan's preferred language: Japanese for `ja` and English for any other or no language. The channel label SHALL be the phase's provider name when it has one, otherwise the channel's name, and a generic ticket label (チケット / Ticket) when the channel is not yet determined. The milestone time SHALL be shown as month, day and hour:minute in the fan's time zone. The link SHALL be the phase's url when it has one and the series page otherwise. Repeated deliveries of the same phase and stage SHALL replace each other on the device, and different stages SHALL NOT.

#### Scenario: Play-guide presale opens

- **WHEN** an `APPLY_OPEN` reminder is built in English for a phase with provider name イープラス opening on 1 July 10:00 in the fan's time zone
- **THEN** the title is Ticket Sales Open and the text is イープラス sales open at Jul 1 10:00

#### Scenario: Channel not determined

- **WHEN** a reminder is built in Japanese for a phase with no provider name and channel `UNSPECIFIED`
- **THEN** the text names the channel as チケット

#### Scenario: No application url

- **WHEN** the phase has no url
- **THEN** the reminder links to the series page

### Requirement: Delivery is delegated to DeliverReminder

ScanDueReminders SHALL NOT deliver reminders or record them as sent; each requested reminder, with its fan, phase, stage and content, SHALL be delivered by DeliverReminder.

#### Scenario: Reminder requested

- **WHEN** ScanDueReminders requests a reminder
- **THEN** DeliverReminder runs once for it and nothing is recorded as sent by the scan
