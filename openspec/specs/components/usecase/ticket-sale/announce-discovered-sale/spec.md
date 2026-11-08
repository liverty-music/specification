# components/usecase/ticket-sale/announce-discovered-sale Specification

## Purpose
TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale tells every fan who is tracking a series that a new ticket sale has been published for it. It runs once for each newly created discovered sale. It sends each recipient a short message in their language that names the opening time, the method and the tour, and opens the recipient's tracked event.

## Requirements

### Requirement: Runs once for each newly created discovered sale

AnnounceDiscoveredSale SHALL run for each discovered sale that TicketSale.UpsertDiscovered announces as created, with that sale and its series as input. An announced sale without a series SHALL be ignored without an error. An Organizer's sale SHALL NOT be announced.

#### Scenario: New discovered sale created
- **WHEN** TicketSale.UpsertDiscovered creates and announces a discovered sale for a series
- **THEN** AnnounceDiscoveredSale runs once for that sale

#### Scenario: Request without a series
- **WHEN** AnnounceDiscoveredSale receives an announced sale that names no series
- **THEN** nothing is announced and it succeeds

#### Scenario: Organizer's sale created
- **WHEN** an Organizer creates a sale with TicketSaleUseCase.Create
- **THEN** AnnounceDiscoveredSale does not run for it

### Requirement: The audience is the fans tracking the series

AnnounceDiscoveredSale SHALL announce the sale to exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the sale's series, and to nobody else; when that list is empty it SHALL succeed without announcing. A fan whose profile cannot be read SHALL be skipped and the others SHALL still be announced to.

#### Scenario: Tracking fan
- **WHEN** ListUserIDsTrackingSeries returns a fan for the series
- **THEN** the fan receives the announcement

#### Scenario: Nobody tracking
- **WHEN** ListUserIDsTrackingSeries returns no fan
- **THEN** nothing is announced and AnnounceDiscoveredSale succeeds

#### Scenario: Profile unreadable
- **WHEN** one of two tracking fans' profile cannot be read
- **THEN** the other fan still receives the announcement

### Requirement: The announcement is sent immediately

AnnounceDiscoveredSale SHALL send the announcement as soon as it runs, whatever the recipient's local time; quiet hours SHALL NOT apply.

#### Scenario: Late evening
- **WHEN** AnnounceDiscoveredSale runs at 23:00 in a recipient's time zone
- **THEN** the recipient is sent the announcement at once

### Requirement: One ticket sale announcement notification requested per recipient

For each recipient AnnounceDiscoveredSale SHALL start NotificationUseCase.Deliver with one notification of type ticket_sale_announcement whose subject is the TicketSale and that recipient's linked event, named after the recipient and the TicketSale, so a recipient is notified of a sale once: a repeated run for the same sale starts nothing new for a recipient already started. Deliver records and delivers each notification on its own, and whether it reaches the recipient's devices does not change the result. When a recipient's notification cannot be started, AnnounceDiscoveredSale SHALL fail so it runs again; the recipients already started are not started again. The story stories/hear-about-a-new-ticket-sale covers the whole flow from discovery to the fan's device.

#### Scenario: Two recipients
- **WHEN** two fans track the series
- **THEN** one ticket_sale_announcement notification is started for each of them

#### Scenario: Request fails
- **WHEN** the notification for the second of three recipients cannot be started
- **THEN** the third recipient's notification is not started, AnnounceDiscoveredSale fails, and when it runs again the second and third recipients are notified and the first is not notified again

#### Scenario: Same sale announced twice
- **WHEN** AnnounceDiscoveredSale runs twice for the same sale and the same recipient
- **THEN** the recipient is notified once

### Requirement: The announcement names the sale and the tour

Each recipient's announcement SHALL be the message the Notification entity renders for a ticket_sale_announcement of the sale, in the recipient's preferred language: it names the sale's method and start time, the artist in its title, and the series title on its last line.

#### Scenario: First-come sale in Japanese
- **WHEN** a FirstCome sale of the series 星降る晩餐会 by Vaundy opens on 6 October 19:00 Asia/Tokyo and the recipient's language is `ja`
- **THEN** the title is [Vaundy] 先着販売のお知らせ and the body is 10/6(火) 19:00から先着販売スタート!! followed by a line break and 星降る晩餐会

#### Scenario: Lottery in English
- **WHEN** a Lottery sale opens on 5 October 18:00 Asia/Tokyo and the recipient's language is `fr`
- **THEN** the title ends with Ticket Lottery and the body is Ticket lottery entry starts Oct 5 (Mon) 18:00! followed by a line break and the series title

### Requirement: The announcement opens the recipient's tracked event

Each recipient's announcement SHALL link to the concert page of that recipient's linked event, as returned by TicketJourney.ListUserIDsTrackingSeries, so that tapping it opens that event's detail sheet. The link and the grouping tag do not depend on the language. Repeated deliveries of the same sale's announcement SHALL replace each other on the device.

#### Scenario: Two fans tracking different shows
- **WHEN** fan A tracks the series' Osaka event and fan B tracks its Tokyo event
- **THEN** fan A's announcement opens the Osaka event and fan B's opens the Tokyo event
