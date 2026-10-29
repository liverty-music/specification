# Spec Delta

## MODIFIED Requirements

### Requirement: The audience is the fans tracking the series

For a discovered sale ScanDueReminders SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the sale's series. For an Organizer's sale it SHALL consider exactly the fans returned by TicketJourney.ListUserIDsTrackingEvents for the events the sale names. Each fan comes with their linked event, and nobody else is considered. A fan whose profile cannot be read SHALL be skipped.

#### Scenario: Tracking fan
- **WHEN** ListUserIDsTrackingSeries returns a fan for the sale's series and a stage is due
- **THEN** a reminder is requested for that fan

#### Scenario: Organizer's sale for some events of the tour
- **WHEN** an Organizer's lottery names the tour's Tokyo event only, fan A tracks the Tokyo event and fan B tracks only the Osaka event
- **THEN** reminders for that lottery are requested for fan A and not for fan B

#### Scenario: Fan no longer listed
- **WHEN** a fan was listed on an earlier run but ListUserIDsTrackingSeries no longer returns them when a lottery's closing reminder becomes due
- **THEN** no `APPLY_CLOSE_24H` reminder is requested for that fan

### Requirement: Reminder content names the sale and the tour

Each requested reminder SHALL carry a title, a text, a link and a grouping tag, in the fan's preferred language: Japanese for `ja`, and English for any other language or none. The title and text SHALL follow the stage and the method as below, where `{start}` and `{end}` are the sale's start and end times, and `{tour}` is the series title. The text SHALL end with a line break followed by `{tour}`. The same content SHALL be used for a discovered sale and for an Organizer's sale.

| stage | method | language | title | text |
|---|---|---|---|---|
| `APPLY_OPEN` | FirstCome | ja | まもなく先着販売開始 | {start}からチケットの先着販売スタート!! |
| `APPLY_OPEN` | FirstCome | en | First-Come Sale Starting Soon | Ticket sale (first come) starts {start}! |
| `APPLY_OPEN` | Lottery | ja | チケット申し込み受付開始 | チケットの抽選申し込みがスタートしました!! 締切は{end} |
| `APPLY_OPEN` | Lottery | en | Ticket Lottery Open | Ticket lottery entry is open! Closes {end}. |
| `APPLY_CLOSE_24H` | Lottery | ja | 抽選の申し込み締切が近づいています | チケットの抽選申し込み締切は{end}!! |
| `APPLY_CLOSE_24H` | Lottery | en | Ticket Lottery Closing Soon | Ticket lottery entry closes {end}! |

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


## ADDED Requirements

### Requirement: A stage is requested from its due time until it expires

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

#### Scenario: Milestone already past when the sale was discovered
- **WHEN** a discovered Lottery sale is discovered at 12:00 on the day its application opened at 10:00
- **THEN** no `APPLY_OPEN` reminder is ever requested for it

#### Scenario: Organizer's sale created after it opened
- **WHEN** an Organizer creates a Lottery sale at 12:00 whose start time was 10:00 the same day and whose end time is 5 days later
- **THEN** an `APPLY_OPEN` reminder is requested for each tracking fan on the next run

#### Scenario: Application window closed before the open reminder was sent
- **WHEN** a fan starts tracking after a Lottery sale's end time and `APPLY_OPEN` was never sent to that fan
- **THEN** no `APPLY_OPEN` reminder is requested for that fan


## REMOVED Requirements

### Requirement: A stage is requested between its due time and its expiry

**Reason**: The `RESULT_DAY` stage is removed: it was due on the day a lottery closed, before any result existed, and a fan of an Organizer's lottery is now told the result directly. A discovered lottery no longer has a result time.
**Migration**: See "A stage is requested from its due time until it expires"; `APPLY_OPEN` and `APPLY_CLOSE_24H` work as before.
