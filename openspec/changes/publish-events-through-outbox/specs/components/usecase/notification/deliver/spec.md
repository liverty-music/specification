## MODIFIED Requirements

### Requirement: Push to every browser of the fan

Deliver SHALL send the message (PushSubscription.Send) to every PushSubscription of the fan (PushSubscription.ListByUserIDs). The outcome SHALL be Delivered, with the time of delivery, when at least one send is accepted, and Failed otherwise: with the reason "no active push subscription" when the fan has none, with the listing error when the subscriptions cannot be read, and with the reason of the last failed send when every send fails. A PushSubscription whose send fails with NotFound SHALL be removed through PushSubscription.Delete, only that fan's browser. When the request is cancelled, no further send SHALL be made; sends already accepted still make the outcome Delivered.

#### Scenario: One of two browsers accepts

- **WHEN** the fan has two browsers and one send is accepted while the other fails
- **THEN** the outcome is Delivered

#### Scenario: No browser registered

- **WHEN** the fan has no PushSubscription
- **THEN** the outcome is Failed with the reason "no active push subscription"

#### Scenario: Every send fails

- **WHEN** every send fails
- **THEN** the outcome is Failed with the reason of the last failure

#### Scenario: Browser gone

- **WHEN** a send fails with NotFound
- **THEN** that PushSubscription is removed and the fan's other browsers keep theirs

#### Scenario: Cancelled after one accepted send

- **WHEN** the request is cancelled after the first of three sends was accepted
- **THEN** the remaining two are not sent and the outcome is Delivered

### Requirement: Runs for each requested notification

Deliver SHALL run once for each notification that NotificationUseCase.NotifyNewConcerts, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale or NotificationUseCase.SendOrderConfirmation starts for one fan, with that fan, the notification type and the finished message; a start repeated under the same name runs nothing new. When a started Deliver fails, that notification SHALL be processed again; a failure for one fan's notification SHALL NOT affect the notifications of any other fan.

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

## REMOVED Requirements

### Requirement: A delivered notification is announced once
**Reason**: Notification.UpdateDelivery announces a Notification it makes Delivered, together with the change (components/entity/notification/update-delivery), so Deliver no longer announces.
**Migration**: Product analytics receives the delivery from that announcement. When the announcement cannot be recorded, UpdateDelivery fails and the Notification stays Queued; by "The outcome is recorded without failing the call", Deliver still succeeds.
