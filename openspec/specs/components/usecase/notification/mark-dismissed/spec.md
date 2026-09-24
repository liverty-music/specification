# Mark Dismissed

## Purpose

NotificationUseCase.MarkDismissed lets a fan dismiss one of their own Notifications. A fan can never change another fan's Notification.

## Requirements

### Requirement: MarkDismissed only for the fan's own notification

MarkDismissed SHALL read the Notification (Notification.Get) and, when it belongs to the fan, mark it dismissed through Notification.MarkDismissed. When no Notification has the id, MarkDismissed SHALL fail with NotFound. When the Notification belongs to another fan, MarkDismissed SHALL fail with PermissionDenied and change nothing.

#### Scenario: Fan dismisses their notification

- **WHEN** a fan dismisses their own Notification
- **THEN** its dismiss time is set and MarkDismissed succeeds

#### Scenario: Another fan's notification

- **WHEN** a fan dismisses a Notification that belongs to another fan
- **THEN** MarkDismissed fails with PermissionDenied and the Notification is unchanged

#### Scenario: Unknown notification

- **WHEN** no Notification has the given id
- **THEN** MarkDismissed fails with NotFound
