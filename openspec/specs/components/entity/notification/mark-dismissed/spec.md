# Notification.MarkDismissed

## Purpose

Records the first time a fan dismissed one of their Notifications.

## Requirements

### Requirement: MarkDismissed sets the dismiss time once, for the fan's own notification

MarkDismissed SHALL set the dismiss time of the Notification with the given id when it belongs to the given fan and has not been dismissed. A repeat call SHALL succeed and keep the first dismiss time. A Notification of another fan, or an unknown id, SHALL be left unchanged and the call SHALL succeed.

#### Scenario: First dismissal

- **WHEN** MarkDismissed runs for the fan's Notification that has not been dismissed
- **THEN** its dismiss time is set

#### Scenario: Dismissed again

- **WHEN** MarkDismissed runs again for the same Notification
- **THEN** the call succeeds and the dismiss time is unchanged

#### Scenario: Another fan's notification

- **WHEN** MarkDismissed runs with a fan who does not own the Notification
- **THEN** the call succeeds and the Notification is unchanged
