## MODIFIED Requirements

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
