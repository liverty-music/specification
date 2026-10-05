# Spec Delta

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: The announcement is generic and links to the series

**Reason**: A generic "new ticket sales information" message asked fans to check details that no screen shows, and it never named the tour. Every fan was also linked to the series' first event, not the one they track.
**Migration**: Replaced by "The announcement names the sale and the tour" and "The announcement opens the recipient's tracked event".
