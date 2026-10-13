# Spec Delta

## Purpose

TicketSaleReminderUseCase.ScanDueReminders runs every 15 minutes. For each TicketSale with a pending milestone, discovered or an Organizer's, it works out which reminder stages have become due for each fan tracking the sale: any event of a discovered sale's series, or an event an Organizer's sale offers. It requests one reminder for each fan, sale and stage not yet sent, with due times adjusted to the fan's time zone and quiet hours, and returns the number of reminders requested.

## ADDED Requirements

### Requirement: Runs every 15 minutes over sales with a pending milestone

ScanDueReminders SHALL run every 15 minutes, which is shorter than the tightest reminder lead (30 minutes before a first-come sale opens). Each run SHALL evaluate the sales returned by TicketSale.ListWithPendingMilestones with a lookahead of 7 days and a lookback of 2 hours, discovered sales and an Organizer's sales alike, and SHALL return the number of reminders it requested. When listing the sales fails, the run SHALL fail; when evaluating one sale fails, that sale SHALL be skipped and the others evaluated.

#### Scenario: Scan cadence
- **WHEN** 15 minutes have passed since the last run
- **THEN** ScanDueReminders runs again

#### Scenario: Sale opening in 3 days
- **WHEN** a sale opens in 3 days
- **THEN** the sale is evaluated on every run from now on

#### Scenario: Organizer's sale is evaluated
- **WHEN** an Organizer's lottery of a Published Series opens in 3 days
- **THEN** the sale is evaluated on every run from now on, like a discovered sale

#### Scenario: One sale fails
- **WHEN** the audience of one sale cannot be read
- **THEN** that sale is skipped and the other sales are evaluated

### Requirement: The audience is the fans tracking the series

For a discovered sale ScanDueReminders SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the sale's series. For an Organizer's sale it SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingEvents for the events the sale offers a TicketType for. Each fan comes with their linked event, and nobody else is considered. A fan whose profile cannot be read SHALL be skipped.

#### Scenario: Tracking fan
- **WHEN** ListUserIDsTrackingSeries returns a fan for the sale's series and a stage is due
- **THEN** a reminder is requested for that fan

#### Scenario: Organizer's sale for some events of the tour
- **WHEN** an Organizer's lottery offers the tour's Tokyo event only, fan A tracks the Tokyo event and fan B tracks only the Osaka event
- **THEN** reminders for that lottery are requested for fan A and not for fan B

#### Scenario: Fan no longer listed
- **WHEN** a fan was listed on an earlier run but ListUserIDsTrackingSeries no longer returns them when the result day arrives
- **THEN** no `RESULT_DAY` reminder is requested for that fan

### Requirement: Delivery is delegated to DeliverReminder

ScanDueReminders SHALL NOT deliver reminders or record them as sent; each requested reminder, with its fan, sale, stage and content, SHALL be delivered by TicketSaleReminderDeliveryUseCase.DeliverReminder.

#### Scenario: Reminder requested
- **WHEN** ScanDueReminders requests a reminder
- **THEN** DeliverReminder runs once for it and nothing is recorded as sent by the scan

### Requirement: A stage is requested between its due time and its expiry

For each fan and each stage that applies to the sale, ScanDueReminders SHALL request a reminder when all of these hold:

- the stage's due time has passed
- the stage has not expired
- TicketSaleReminder.ListSentStages does not show that stage as sent to that fan

The due time of `APPLY_OPEN` and `APPLY_CLOSE_24H` SHALL be the stage's anchor. The due time of `RESULT_DAY` SHALL be 09:00 in the fan's time zone on the calendar day, in that time zone, of the sale's result time. For a discovered sale, a stage whose anchor is earlier than the sale's discovered time SHALL NOT be requested.

A stage expires as follows:

| stage | method | expires at |
|---|---|---|
| `APPLY_OPEN` | FirstCome | the start time |
| `APPLY_OPEN` | Lottery | the end time |
| `APPLY_CLOSE_24H` | Lottery | the end time |
| `RESULT_DAY` | Lottery | the end of the calendar day, in the fan's time zone, of the result time |

A fan who starts tracking after a stage's due time but before it expires SHALL still be reminded of it on the next run while the sale is listed. A fan who starts tracking after a stage has expired SHALL NOT be reminded of it.

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

#### Scenario: Result day
- **WHEN** a sale's result time is 15 July 18:00 and the fan's time zone is Asia/Tokyo
- **THEN** the `RESULT_DAY` reminder becomes due at 15 July 09:00 Asia/Tokyo

#### Scenario: Organizer's lottery result day
- **WHEN** an Organizer's Lottery sale ends on 12 October 23:59 and the fan's time zone is Asia/Tokyo
- **THEN** the `RESULT_DAY` reminder becomes due at 12 October 09:00 Asia/Tokyo

#### Scenario: Milestone already past when the sale was discovered
- **WHEN** a discovered Lottery sale is discovered at 12:00 on the day its application opened at 10:00
- **THEN** no `APPLY_OPEN` reminder is ever requested for it

#### Scenario: Organizer's sale created after it opened
- **WHEN** an Organizer creates a Lottery sale at 12:00 whose start time was 10:00 the same day and whose end time is 5 days later
- **THEN** an `APPLY_OPEN` reminder is requested for each tracking fan on the next run

#### Scenario: Application window closed before the open reminder was sent
- **WHEN** a fan starts tracking after a Lottery sale's end time and `APPLY_OPEN` was never sent to that fan
- **THEN** no `APPLY_OPEN` reminder is requested for that fan

#### Scenario: Result day has ended
- **WHEN** the current time is past the end of the result day in the fan's time zone and `RESULT_DAY` was never sent to that fan
- **THEN** no `RESULT_DAY` reminder is requested for that fan

### Requirement: Quiet hours by stage

ScanDueReminders SHALL NOT send a reminder in the fan's quiet window, 22:00 to 08:00 in the fan's time zone, falling back to Asia/Tokyo when the fan's time zone is unset or not recognised. A stage due inside the window SHALL move as follows:

- A FirstCome sale's `APPLY_OPEN` moves earlier, to 21:00 just before that window begins, so it still arrives before the sale opens.
- Every other stage moves later, to the next 08:00.

#### Scenario: First-come sale at midnight
- **WHEN** a FirstCome sale opens at 00:00, so its `APPLY_OPEN` anchor is 23:30
- **THEN** the reminder becomes due at 21:00 that evening

#### Scenario: Lottery opening during the night
- **WHEN** a Lottery sale opens at 02:00 in the fan's time zone
- **THEN** its `APPLY_OPEN` reminder becomes due at 08:00 that morning

#### Scenario: Close reminder at night
- **WHEN** a Lottery sale closes at 23:59, so its `APPLY_CLOSE_24H` anchor is 23:59 the day before
- **THEN** the reminder becomes due at 08:00 on the closing day

#### Scenario: Time zone fallback
- **WHEN** a fan's time zone is unset or not a recognised time zone
- **THEN** the quiet window and due times are evaluated in Asia/Tokyo

### Requirement: Reminder content names the sale and the tour

Each requested reminder SHALL carry a title, a text, a link and a grouping tag, in the fan's preferred language: Japanese for `ja`, and English for any other language or none. The title and text SHALL follow the stage and the method as below, where `{start}`, `{end}` and `{result}` are the sale's start, end and result times, and `{tour}` is the series title. The text SHALL end with a line break followed by `{tour}`. The same content SHALL be used for a discovered sale and for an Organizer's sale.

| stage | method | language | title | text |
|---|---|---|---|---|
| `APPLY_OPEN` | FirstCome | ja | まもなく先着販売開始 | {start}からチケットの先着販売スタート!! |
| `APPLY_OPEN` | FirstCome | en | First-Come Sale Starting Soon | Ticket sale (first come) starts {start}! |
| `APPLY_OPEN` | Lottery | ja | チケット申し込み受付開始 | チケットの抽選申し込みがスタートしました!! 締切は{end} |
| `APPLY_OPEN` | Lottery | en | Ticket Lottery Open | Ticket lottery entry is open! Closes {end}. |
| `APPLY_CLOSE_24H` | Lottery | ja | 抽選の申し込み締切が近づいています | チケットの抽選申し込み締切は{end}!! |
| `APPLY_CLOSE_24H` | Lottery | en | Ticket Lottery Closing Soon | Ticket lottery entry closes {end}! |
| `RESULT_DAY` | Lottery | ja | 本日 抽選結果発表 | 本日{result}にチケットの抽選結果発表!! |
| `RESULT_DAY` | Lottery | en | Lottery Results Today | Ticket lottery results are out today at {result}! |

Times SHALL be shown in the fan's time zone. In Japanese they are month/day(weekday) hour:minute, for example `10/22(木) 23:59`. In English they are month day (weekday) hour:minute, for example `Oct 22 (Thu) 23:59`.

The link SHALL be the concert page of the fan's linked event as returned by TicketJourney.ListUserIDsTrackingSeries or TicketJourney.ListUserIDsTrackingEvents. Repeated deliveries of the same sale and stage SHALL replace each other on the device, and different stages SHALL NOT.

#### Scenario: Lottery closing in Japanese
- **WHEN** an `APPLY_CLOSE_24H` reminder is built in Japanese for the series King Gnu 10th Anniversary Opening Live “KICKOFF”, whose lottery closes on 22 October 23:59 Asia/Tokyo
- **THEN** the title is 抽選の申し込み締切が近づいています and the text is チケットの抽選申し込み締切は10/22(木) 23:59!! followed by a line break and the series title

#### Scenario: Deferred close reminder keeps the absolute deadline
- **WHEN** an `APPLY_CLOSE_24H` reminder is deferred to 08:00 on the closing day
- **THEN** its text still states the end time, and nothing in it says how many hours are left

#### Scenario: Link to the tracked event
- **WHEN** a fan's linked event in the series is its 1 November event
- **THEN** the reminder links to the concert page of the 1 November event
