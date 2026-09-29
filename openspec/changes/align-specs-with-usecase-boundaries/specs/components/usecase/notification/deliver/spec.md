# Spec Delta

## ADDED Requirements

### Requirement: Runs for each requested notification

Deliver SHALL run once for each notification requested for one fan, by PushNotificationUseCase.NotifyNewConcerts or SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase, with that fan, the notification type and the finished message. When Deliver fails, that request SHALL be processed again; a failure for one fan's request SHALL NOT affect the requests of any other fan.

#### Scenario: Notification requested

- **WHEN** a new_concerts notification is requested for a fan
- **THEN** Deliver runs for that fan with the type new_concerts and the requested message

#### Scenario: Recording fails for one request

- **WHEN** Deliver fails because the Notification for one of three requested fans cannot be recorded
- **THEN** that fan's request is processed again and the other two fans' requests are unaffected

## MODIFIED Requirements

### Requirement: No record, no send

Deliver SHALL take a fan, a notification type and a finished message. It SHALL fail with InvalidArgument when no message is given. It SHALL record the Notification through Notification.Create before sending anything; when recording fails, Deliver SHALL fail with that error and send nothing, so the request is processed again.

#### Scenario: Missing message

- **WHEN** Deliver is called without a message
- **THEN** it fails with InvalidArgument and nothing is recorded or sent

#### Scenario: Recording fails

- **WHEN** the Notification cannot be recorded
- **THEN** Deliver fails and no browser is sent the message

### Requirement: The pushed message carries the notification id

Before sending, Deliver SHALL add the recorded Notification's id to the message's data, keeping the rest of the message unchanged, and send that same message to each of the fan's browsers.

#### Scenario: Message identifies its notification

- **WHEN** a Notification is recorded with a new id
- **THEN** the message pushed to every browser of the fan carries that id

### Requirement: Push to every browser of the fan

Deliver SHALL send the message (PushSubscription.Send) to every PushSubscription of the fan (PushSubscription.ListByUserIDs). The outcome SHALL be Delivered, with the time of delivery, when at least one send is accepted, and Failed otherwise: with the reason "no active push subscription" when the fan has none, with the listing error when the subscriptions cannot be read, and with the reason of the last failed send when every send fails. A PushSubscription whose send fails with NotFound SHALL be removed through PushSubscription.Delete, only that fan's browser; this removal is not announced as an unsubscription. When the request is cancelled, no further send SHALL be made; sends already accepted still make the outcome Delivered.

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

### Requirement: The outcome is recorded without failing the call

Deliver SHALL record the outcome through Notification.UpdateDelivery and return the Notification with that outcome. A failure to record the outcome SHALL NOT fail Deliver; the stored Notification may then stay Queued. A failed delivery SHALL NOT fail Deliver either.

#### Scenario: Delivery failed

- **WHEN** every send fails
- **THEN** Deliver succeeds and the stored Notification is Failed with its reason

#### Scenario: Outcome cannot be stored

- **WHEN** the send is accepted but the outcome cannot be recorded
- **THEN** Deliver succeeds, returns the Notification as Delivered, and the stored Notification stays Queued

### Requirement: A delivered notification is announced once

When the outcome is Delivered, Deliver SHALL announce once that the fan's Notification of that type was delivered. A failure to announce SHALL NOT change the outcome or fail Deliver. A Failed Notification is not announced.

#### Scenario: Delivered

- **WHEN** the outcome is Delivered
- **THEN** the delivery is announced once

#### Scenario: Failed

- **WHEN** the outcome is Failed
- **THEN** nothing is announced
