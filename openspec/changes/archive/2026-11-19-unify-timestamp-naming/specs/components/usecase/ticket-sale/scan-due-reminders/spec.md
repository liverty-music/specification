# Spec Delta

## MODIFIED Requirements

### Requirement: A stage is requested while it is due

For each fan and each stage that applies to the sale, ScanDueReminders SHALL request a reminder when all of these hold:

- the stage's due time has passed
- the stage has not expired
- TicketSaleReminder.ListSentStages does not show that stage as sent to that fan

The due time of a stage SHALL be its anchor. For a discovered sale, a stage whose anchor is earlier than the sale's find time SHALL NOT be requested.

A stage expires as follows:

| stage | method | expires at |
|---|---|---|
| `APPLY_OPEN` | FirstCome | the start time |
| `APPLY_OPEN` | Lottery | the end time |
| `APPLY_CLOSE_24H` | Lottery | the end time |

A fan who joins the stage's audience after a stage's due time but before it expires SHALL still be reminded of it on the next run while the sale is listed. A fan who joins it after a stage has expired SHALL NOT be reminded of it.

When the sent stages cannot be read, ScanDueReminders SHALL request the due reminders anyway and rely on DeliverReminder not to repeat a sent one. A request that cannot be queued SHALL be skipped and retried by a later run.

#### Scenario: First-come sale about to open
- **WHEN** a FirstCome sale opens at 19:00 and the time is 18:30
- **THEN** an `APPLY_OPEN` reminder is requested for each tracking fan

#### Scenario: First-come sale already open
- **WHEN** a fan starts tracking at 19:05 a FirstCome sale that opened at 19:00
- **THEN** no `APPLY_OPEN` reminder is requested for that fan

#### Scenario: Lottery opens
- **WHEN** a Lottery sale's start time has just passed and `APPLY_OPEN` was not sent to a tracking fan
- **THEN** an `APPLY_OPEN` reminder is requested for the fan

#### Scenario: Already sent
- **WHEN** `APPLY_OPEN` was already recorded as sent to the fan
- **THEN** no reminder is requested again

#### Scenario: Milestone already past when the sale was discovered
- **WHEN** a discovered Lottery sale is discovered at 12:00 on the day its application opened at 10:00
- **THEN** no `APPLY_OPEN` reminder is ever requested for it

#### Scenario: Organizer's sale created after it opened
- **WHEN** an Organizer creates a Lottery sale at 12:00 whose start time was 10:00 the same day and whose end time is 5 days later
- **THEN** an `APPLY_OPEN` reminder is requested for each tracking fan on the next run

#### Scenario: Application window closed before the open reminder was sent
- **WHEN** a fan starts tracking after a Lottery sale's end time and `APPLY_OPEN` was never sent to that fan
- **THEN** no `APPLY_OPEN` reminder is requested for that fan
