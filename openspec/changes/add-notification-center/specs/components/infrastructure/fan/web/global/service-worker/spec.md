## ADDED Requirements

### Requirement: Opening a push notification marks it read

When a fan opens a push notification, the app SHALL open the notification's link and mark that Notification read (NotificationUseCase.MarkRead) for the signed-in fan. When the fan is not signed in, or marking fails, the link SHALL still open and the Notification stays unread.

#### Scenario: Open a lottery loss notification
- **WHEN** a signed-in fan opens the push of an unread lottery_loss Notification
- **THEN** the event's page opens and the Notification is read in the notification center

#### Scenario: Marking fails
- **WHEN** marking the Notification read fails
- **THEN** the event's page still opens and the Notification stays unread
