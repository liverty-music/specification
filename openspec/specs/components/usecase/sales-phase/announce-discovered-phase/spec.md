# Announce Discovered Phase

## Purpose

AnnounceDiscoveredPhase tells every fan who is tracking a series that a new ticket sales phase has been published for it. It runs once for each newly created sales phase. It sends each recipient a short message in their language that names the opening time, the method and the tour, and opens the recipient's tracked event.

## Requirements

### Requirement: Runs once for each newly created sales phase

AnnounceDiscoveredPhase SHALL run when DiscoverForArtist requests the announcement of a sales phase it has just created, with that phase and its series as input. A request without a series SHALL be ignored without an error.

#### Scenario: New phase created

- **WHEN** DiscoverForArtist creates a sales phase for a series
- **THEN** AnnounceDiscoveredPhase runs once for that phase

#### Scenario: Request without a series

- **WHEN** AnnounceDiscoveredPhase receives a request that names no series
- **THEN** nothing is announced and it succeeds

### Requirement: The audience is the fans tracking the series

AnnounceDiscoveredPhase SHALL announce the phase to exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the phase's series, and to nobody else; when that list is empty it SHALL succeed without announcing. A fan whose profile cannot be read SHALL be skipped and the others SHALL still be announced to.

#### Scenario: Tracking fan

- **WHEN** ListUserIDsTrackingSeries returns a fan for the series
- **THEN** the fan receives the announcement

#### Scenario: Nobody tracking

- **WHEN** ListUserIDsTrackingSeries returns no fan
- **THEN** nothing is announced and AnnounceDiscoveredPhase succeeds

#### Scenario: Profile unreadable

- **WHEN** one of two tracking fans' profile cannot be read
- **THEN** the other fan still receives the announcement

### Requirement: The announcement is sent immediately

AnnounceDiscoveredPhase SHALL send the announcement as soon as it runs, whatever the recipient's local time; quiet hours SHALL NOT apply.

#### Scenario: Late evening

- **WHEN** AnnounceDiscoveredPhase runs at 23:00 in a recipient's time zone
- **THEN** the recipient is sent the announcement at once

### Requirement: One sales-phase announcement notification requested per recipient

For each recipient AnnounceDiscoveredPhase SHALL request one notification of type sales-phase announcement carrying that recipient's message; NotificationUseCase.Deliver records and delivers each requested notification afterwards, for each recipient on its own, and whether it reaches the recipient's devices does not change the result. When a recipient's request cannot be made, AnnounceDiscoveredPhase SHALL fail so the whole announcement runs again; a request repeated within 2 minutes for the same phase and recipient SHALL reach the recipient only once, and a later repeat replaces the earlier one on their device. The story stories/hear-about-a-new-ticket-sale covers the whole flow from discovery to the fan's device.

#### Scenario: Two recipients

- **WHEN** two fans track the series
- **THEN** one sales-phase announcement notification is requested for each of them

#### Scenario: Request fails

- **WHEN** the notification for the second of three recipients cannot be requested
- **THEN** the third recipient's notification is not requested, AnnounceDiscoveredPhase fails, and the announcement runs again for all three recipients

#### Scenario: Same phase announced twice

- **WHEN** AnnounceDiscoveredPhase runs twice within 2 minutes for the same phase and the same recipient
- **THEN** the recipient's two requests are the same request and the recipient receives the announcement once

### Requirement: The announcement names the sale and the tour

Each recipient's announcement SHALL be in the recipient's preferred language: Japanese for `ja`, and English for any other language or none. Its title and text SHALL follow the phase's method as below, where `{start}` is the apply start time and `{tour}` is the series title. The text SHALL end with a line break followed by `{tour}`.

| method | language | title | text |
|---|---|---|---|
| `FIRST_COME` | ja | チケット先着販売のお知らせ | {start}からチケットの先着販売スタート!! |
| `FIRST_COME` | en | First-Come Ticket Sale | Ticket sale (first come) starts {start}! |
| `LOTTERY` | ja | チケット抽選受付のお知らせ | {start}からチケットの抽選申し込みスタート!! |
| `LOTTERY` | en | Ticket Lottery | Ticket lottery entry starts {start}! |

`{start}` SHALL be shown in the recipient's time zone, falling back to Asia/Tokyo when it is unset or not recognised. In Japanese it is month/day(weekday) hour:minute, for example `10/6(火) 19:00`. In English it is month day (weekday) hour:minute, for example `Oct 6 (Tue) 19:00`.

#### Scenario: First-come sale in Japanese

- **WHEN** a `FIRST_COME` phase of the series 星降る晩餐会 opens on 6 October 19:00 Asia/Tokyo and the recipient's language is `ja`
- **THEN** the title is チケット先着販売のお知らせ and the text is 10/6(火) 19:00からチケットの先着販売スタート!! followed by a line break and 星降る晩餐会

#### Scenario: Lottery in English

- **WHEN** a `LOTTERY` phase opens on 5 October 18:00 Asia/Tokyo and the recipient's language is `fr`
- **THEN** the title is Ticket Lottery and the text is Ticket lottery entry starts Oct 5 (Mon) 18:00! followed by a line break and the series title

### Requirement: The announcement opens the recipient's tracked event

Each recipient's announcement SHALL link to the concert page of that recipient's linked event, as returned by TicketJourney.ListUserIDsTrackingSeries, so that tapping it opens that event's detail sheet. The link and the grouping tag do not depend on the language. Repeated deliveries of the same phase's announcement SHALL replace each other on the device.

#### Scenario: Two fans tracking different shows

- **WHEN** fan A tracks the series' Osaka event and fan B tracks its Tokyo event
- **THEN** fan A's announcement opens the Osaka event and fan B's opens the Tokyo event
