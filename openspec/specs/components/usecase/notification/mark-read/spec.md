# Mark Read

## Purpose

NotificationUseCase.MarkRead lets a fan mark one of their own Notifications as read. A fan can never change another fan's Notification.

## Requirements

### Requirement: MarkRead only for the fan's own notification

MarkRead SHALL read the Notification (Notification.Get) and, when it belongs to the fan, mark it read through Notification.MarkRead. When no Notification has the id, MarkRead SHALL fail with NotFound. When the Notification belongs to another fan, MarkRead SHALL fail with PermissionDenied and change nothing.

#### Scenario: Fan reads their notification

- **WHEN** a fan marks their own Notification as read
- **THEN** its read time is set and MarkRead succeeds

#### Scenario: Another fan's notification

- **WHEN** a fan marks a Notification that belongs to another fan
- **THEN** MarkRead fails with PermissionDenied and the Notification is unchanged

#### Scenario: Unknown notification

- **WHEN** no Notification has the given id
- **THEN** MarkRead fails with NotFound
