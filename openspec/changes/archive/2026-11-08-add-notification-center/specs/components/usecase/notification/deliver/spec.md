## MODIFIED Requirements

### Requirement: The pushed message carries the notification id

Before sending, Deliver SHALL add the recorded Notification's id and its type to the rendered message's data, keeping the rest of the message unchanged, and send that same message to each of the fan's browsers. A sales_reminder message's data SHALL also name its TicketSale and reminder stage.

#### Scenario: Message identifies its notification

- **WHEN** a Notification is recorded with a new id
- **THEN** the message pushed to every browser of the fan carries that id

#### Scenario: Message names its type

- **WHEN** Deliver records a Notification of type sales_reminder
- **THEN** the message pushed to every browser of the fan carries the type sales_reminder, its TicketSale and its stage

### Requirement: Push to every browser of the fan

Deliver SHALL send the message (PushSubscription.Send) to every PushSubscription of the fan (PushSubscription.ListByUserIDs). The outcome SHALL be Delivered when at least one send is accepted, and Failed otherwise: with the reason "no active push subscription" when the fan has none, with the listing error when the subscriptions cannot be read, and with the reason of the last failed send when every send fails. A PushSubscription whose send fails with NotFound SHALL be removed through PushSubscription.DeleteGone, only that fan's browser, so the removal is not counted as the fan unsubscribing. When the request is cancelled, no further send SHALL be made; sends already accepted still make the outcome Delivered.

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
- **THEN** that PushSubscription is removed without an unsubscription being announced, and the fan's other browsers keep theirs

#### Scenario: Cancelled after one accepted send

- **WHEN** the request is cancelled after the first of three sends was accepted
- **THEN** the remaining two are not sent and the outcome is Delivered

### Requirement: Runs for each requested notification

Deliver SHALL run once for each notification that NotificationUseCase.NotifyNewConcerts, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale, TicketSaleReminderDeliveryUseCase.DeliverReminder, NotificationUseCase.SendOrderConfirmation, NotificationUseCase.SendLotteryLoss, NotificationUseCase.SendResaleEntryEnded, NotificationUseCase.SendEventCancelled or NotificationUseCase.SendOrderRefunded starts for one fan, with that fan, the notification type and the subject; a start repeated under the same name runs nothing new. When a started Deliver fails, that notification SHALL be processed again; a failure for one fan's notification SHALL NOT affect the notifications of any other fan.

#### Scenario: Notification requested

- **WHEN** NotifyNewConcerts starts a new_concerts notification for a fan
- **THEN** Deliver runs for that fan with the type new_concerts and the requested subject

#### Scenario: Purchase notification requested

- **WHEN** SendOrderConfirmation starts the push of a won lottery entry's Order
- **THEN** Deliver runs for the Order's user with the type lottery_win

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

#### Scenario: Cancellation sent

- **WHEN** SendEventCancelled starts the push telling a fan their concert is cancelled
- **THEN** Deliver runs for the Order's user with the type concert_cancelled

#### Scenario: Refund sent

- **WHEN** SendOrderRefunded starts the push telling a fan their Order was refunded
- **THEN** Deliver runs for the Order's user with the type order_refunded

## ADDED Requirements

### Requirement: Render and record before sending

Deliver SHALL take a fan, a notification type and a subject. It SHALL fail with InvalidArgument when the subject is invalid for the type. It SHALL read the records the subject names and the fan's follows, and render the Notification's message, before recording or sending anything. When a record the subject names no longer exists, Deliver SHALL record and send nothing, and succeed with the outcome Failed and the reason "subject no longer exists". When another read fails, Deliver SHALL fail with that error and send nothing, so the request is processed again. It SHALL then record the Notification through Notification.Create before sending anything; when recording fails, Deliver SHALL fail with that error and send nothing, so the request is processed again.

#### Scenario: Subject missing a record

- **WHEN** Deliver is called for type lottery_loss without a LotteryEntry
- **THEN** it fails with InvalidArgument and nothing is recorded or sent

#### Scenario: Subject deleted before delivery

- **WHEN** the Order a concert_cancelled request names no longer exists
- **THEN** nothing is recorded or sent and Deliver succeeds with Failed and the reason "subject no longer exists"

#### Scenario: Recording fails

- **WHEN** the Notification cannot be recorded
- **THEN** Deliver fails and no browser is sent the message


### Requirement: The outcome is returned and logged, not stored

Deliver SHALL return the outcome, with its failure reason when Failed, to its caller, and SHALL log it for usage analytics with the fan, the type and, when one was recorded, the Notification's id. The outcome SHALL NOT be stored on the Notification, and a Failed outcome SHALL NOT fail Deliver.

#### Scenario: Delivery failed

- **WHEN** every send fails
- **THEN** Deliver succeeds, returns Failed with the reason, and the stored Notification is unchanged

#### Scenario: Delivered

- **WHEN** a send is accepted
- **THEN** Deliver returns Delivered and logs the delivery for analytics

## REMOVED Requirements

### Requirement: No record, no send
**Reason**: Replaced by "Render and record before sending", which states the behavior without the scenarios of the removed behavior.
**Migration**: None.


### Requirement: The outcome is recorded without failing the call
**Reason**: A Notification no longer records its delivery outcome.
**Migration**: See "The outcome is returned and logged, not stored".
