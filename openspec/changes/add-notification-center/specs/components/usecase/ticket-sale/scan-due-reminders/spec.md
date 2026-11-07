## ADDED Requirements

### Requirement: A reminder's message names the sale and the tour

Each reminder's message SHALL be the one the Notification entity renders for a sales_reminder of the sale, the stage and the fan's linked event, in the fan's preferred language: it names the stage, the start or end time, the artist in its title and the series title on its last line. The same message SHALL be used for a discovered sale and for an Organizer's sale. The link SHALL be the concert page of the fan's linked event as returned by TicketJourney.ListUserIDsTrackingSeries or TicketJourney.ListUserIDsTrackingEvents.

#### Scenario: Lottery closing in Japanese
- **WHEN** an `APPLY_CLOSE_24H` reminder is built in Japanese for the series King Gnu 10th Anniversary Opening Live “KICKOFF” by King Gnu, whose lottery closes on 22 October 23:59 Asia/Tokyo
- **THEN** the title is [King Gnu] 抽選締切が近づいています and the body is 抽選申し込みの締切は10/22(木) 23:59!! followed by a line break and the series title

#### Scenario: Deferred close reminder keeps the absolute deadline
- **WHEN** an `APPLY_CLOSE_24H` reminder is deferred to 08:00 on the closing day
- **THEN** its body still states the end time, and nothing in it says how many hours are left

#### Scenario: Link to the tracked event
- **WHEN** a fan's linked event in the series is its 1 November event
- **THEN** the reminder links to the concert page of the 1 November event

### Requirement: A stage is requested while it is due

For each fan and each stage that applies to the sale, ScanDueReminders SHALL request a reminder when all of these hold:

- the stage's due time has passed
- the stage has not expired
- TicketSaleReminder.ListSentStages does not show that stage as sent to that fan

The due time of a stage SHALL be its anchor. For a discovered sale, a stage whose anchor is earlier than the sale's discovered time SHALL NOT be requested.

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

### Requirement: The audience is the fans tracking the sale

For each stage of a discovered sale ScanDueReminders SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the sale's series. For an Organizer's sale it SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingEvents for the events the sale names. Each fan comes with their linked event, and nobody else is considered. A fan whose profile cannot be read SHALL be skipped.

#### Scenario: Tracking fan
- **WHEN** ListUserIDsTrackingSeries returns a fan for the sale's series and the `APPLY_OPEN` stage is due
- **THEN** a reminder is requested for that fan

#### Scenario: Organizer's sale for some events of the tour
- **WHEN** an Organizer's lottery names the tour's Tokyo event only, fan A tracks the Tokyo event and fan B tracks only the Osaka event
- **THEN** reminders for that lottery are requested for fan A and not for fan B

#### Scenario: Fan no longer listed
- **WHEN** a fan was listed on an earlier run but ListUserIDsTrackingSeries no longer returns them when a lottery's closing reminder becomes due
- **THEN** no `APPLY_CLOSE_24H` reminder is requested for that fan

## MODIFIED Requirements

### Requirement: Delivery is delegated to DeliverReminder

ScanDueReminders SHALL NOT deliver reminders or record them as sent; it SHALL start TicketSaleReminderDeliveryUseCase.DeliverReminder for each requested reminder, with its fan, sale, stage and the fan's linked event. Each start SHALL be named after the fan, the sale, the stage and the 15-minute period the run belongs to, so a run repeated in the same period starts no reminder twice, and a later run starts the reminder again while it is not recorded as sent.

#### Scenario: Reminder requested
- **WHEN** ScanDueReminders requests a reminder
- **THEN** DeliverReminder runs once for it and nothing is recorded as sent by the scan

#### Scenario: Run repeated in the same period
- **WHEN** the run of 18:30 is repeated at 18:37 and requests the same reminder again
- **THEN** DeliverReminder runs once for that fan, sale and stage

#### Scenario: Not yet recorded as sent
- **WHEN** the run of 18:30 requested a reminder whose push failed, and the run of 18:45 finds the stage still due and not recorded as sent
- **THEN** DeliverReminder runs again for that fan, sale and stage

## REMOVED Requirements

### Requirement: Reminder content names the sale and the tour
**Reason**: The result-day reminder is removed; replaced by "A reminder's message names the sale and the tour".
**Migration**: None.

### Requirement: A stage is requested from its due time until it expires
**Reason**: The result-day reminder is removed; replaced by "A stage is requested while it is due".
**Migration**: None.

### Requirement: The audience is the fans tracking or applied for the series
**Reason**: The result-day reminder and its audience of applied fans are removed; replaced by "The audience is the fans tracking the sale".
**Migration**: None.
