## MODIFIED Requirements

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

### Requirement: One ticket sale announcement notification requested per recipient

For each recipient AnnounceDiscoveredSale SHALL start NotificationUseCase.Deliver with one notification of type ticket_sale_announcement carrying that recipient's message, named after the recipient and the TicketSale, so a recipient is notified of a sale once: a repeated run for the same sale starts nothing new for a recipient already started. Deliver records and delivers each notification on its own, and whether it reaches the recipient's devices does not change the result. When a recipient's notification cannot be started, AnnounceDiscoveredSale SHALL fail so it runs again; the recipients already started are not started again. The story stories/hear-about-a-new-ticket-sale covers the whole flow from discovery to the fan's device.

#### Scenario: Two recipients
- **WHEN** two fans track the series
- **THEN** one ticket_sale_announcement notification is started for each of them

#### Scenario: Request fails
- **WHEN** the notification for the second of three recipients cannot be started
- **THEN** the third recipient's notification is not started, AnnounceDiscoveredSale fails, and when it runs again the second and third recipients are notified and the first is not notified again

#### Scenario: Same sale announced twice
- **WHEN** AnnounceDiscoveredSale runs twice for the same sale and the same recipient
- **THEN** the recipient is notified once
