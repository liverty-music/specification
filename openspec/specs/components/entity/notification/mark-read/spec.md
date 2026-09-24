# Notification.MarkRead

## Purpose

Records the first time a fan read one of their Notifications.

## Requirements

### Requirement: MarkRead sets the read time once, for the fan's own notification

MarkRead SHALL set the read time of the Notification with the given id when it belongs to the given fan and has not been read. A repeat call SHALL succeed and keep the first read time. A Notification of another fan, or an unknown id, SHALL be left unchanged and the call SHALL succeed.

#### Scenario: First read

- **WHEN** MarkRead runs for the fan's unread Notification
- **THEN** its read time is set

#### Scenario: Read again

- **WHEN** MarkRead runs again for the same Notification
- **THEN** the call succeeds and the read time is unchanged

#### Scenario: Another fan's notification

- **WHEN** MarkRead runs with a fan who does not own the Notification
- **THEN** the call succeeds and the Notification is unchanged
