# Spec Delta

## MODIFIED Requirements

### Requirement: Runs for each requested notification

Deliver SHALL run once for each notification requested for one fan, by PushNotificationUseCase.NotifyNewConcerts, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale or NotificationUseCase.SendOrderConfirmation, with that fan, the notification type and the finished message. When Deliver fails, that request SHALL be processed again; a failure for one fan's request SHALL NOT affect the requests of any other fan.

#### Scenario: Notification requested

- **WHEN** a new_concerts notification is requested for a fan
- **THEN** Deliver runs for that fan with the type new_concerts and the requested message

#### Scenario: Purchase notification requested

- **WHEN** an order_confirmation notification is requested for a buyer
- **THEN** Deliver runs for that buyer with the type order_confirmation

#### Scenario: Recording fails for one request

- **WHEN** Deliver fails because the Notification for one of three requested fans cannot be recorded
- **THEN** that fan's request is processed again and the other two fans' requests are unaffected

#### Scenario: Discovered sale announced

- **WHEN** a ticket_sale_announcement notification is requested for a fan
- **THEN** Deliver runs for that fan with the type ticket_sale_announcement
