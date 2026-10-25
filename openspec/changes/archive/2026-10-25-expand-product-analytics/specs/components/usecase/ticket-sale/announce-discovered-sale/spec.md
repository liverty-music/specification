## MODIFIED Requirements

### Requirement: One ticket sale announcement notification requested per recipient

For each recipient AnnounceDiscoveredSale SHALL request one notification of type ticket_sale_announcement carrying that recipient's message; NotificationUseCase.Deliver records and delivers each requested notification afterwards, for each recipient on its own, and whether it reaches the recipient's devices does not change the result. When a recipient's request cannot be made, AnnounceDiscoveredSale SHALL fail so the whole announcement runs again; a repeated request for the same sale and recipient is a new request, so the recipient can receive the announcement again; the later one replaces the earlier one on their device. Requesting once per sale and recipient waits for a follow-up change (design, "One kind of CloudEvent id"). The story stories/hear-about-a-new-ticket-sale covers the whole flow from discovery to the fan's device.

#### Scenario: Two recipients
- **WHEN** two fans track the series
- **THEN** one ticket_sale_announcement notification is requested for each of them

#### Scenario: Request fails
- **WHEN** the notification for the second of three recipients cannot be requested
- **THEN** the third recipient's notification is not requested, AnnounceDiscoveredSale fails, and the announcement runs again for all three recipients

#### Scenario: Same sale announced twice
- **WHEN** AnnounceDiscoveredSale runs twice within 2 minutes for the same sale and the same recipient
- **THEN** two requests are made for the recipient, and the second replaces the first on the recipient's device
