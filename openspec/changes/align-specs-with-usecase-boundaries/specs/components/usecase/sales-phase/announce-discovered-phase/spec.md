# Spec Delta

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: One sales-phase announcement notification per recipient

**Reason**: AnnounceDiscoveredPhase no longer records or sends the notifications itself. It requests one per recipient, and NotificationUseCase.Deliver records and sends each on its own, so a recording failure for one recipient no longer fails the announcement.

**Migration**: Replaced by "One sales-phase announcement notification requested per recipient"; recording and sending are stated in components/usecase/notification/deliver.
