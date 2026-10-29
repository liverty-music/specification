## MODIFIED Requirements

### Requirement: Runs for each requested notification

Deliver SHALL run once for each notification that NotificationUseCase.NotifyNewConcerts, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale, NotificationUseCase.SendOrderConfirmation, NotificationUseCase.SendLotteryLoss or NotificationUseCase.SendResaleEntryEnded starts for one fan, with that fan, the notification type and the finished message; a start repeated under the same name runs nothing new. When a started Deliver fails, that notification SHALL be processed again; a failure for one fan's notification SHALL NOT affect the notifications of any other fan.

#### Scenario: Notification requested

- **WHEN** NotifyNewConcerts starts a new_concerts notification for a fan
- **THEN** Deliver runs for that fan with the type new_concerts and the requested message

#### Scenario: Purchase notification requested

- **WHEN** SendOrderConfirmation starts the push of an Order's confirmation
- **THEN** Deliver runs for the Order's user with the type order_confirmation

#### Scenario: Recording fails for one request

- **WHEN** Deliver fails because the Notification for one of three started fans cannot be recorded
- **THEN** that fan's notification is processed again and the other two fans' notifications are unaffected

#### Scenario: Discovered sale announced

- **WHEN** AnnounceDiscoveredSale starts a ticket_sale_announcement notification for a fan
- **THEN** Deliver runs for that fan with the type ticket_sale_announcement

#### Scenario: Lottery loss sent

- **WHEN** SendLotteryLoss starts the push telling a fan their entry lost
- **THEN** Deliver runs for the fan of the entry's Order with the type lottery_loss

#### Scenario: Resale entry ended

- **WHEN** SendResaleEntryEnded starts the push telling a fan their resale entry lapsed
- **THEN** Deliver runs for that fan with the type resale_entry_lapsed
