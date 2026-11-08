# components/usecase/notification/list Specification

## Purpose
NotificationUseCase.List returns the 50 newest Notifications of a fan, each rendered in the fan's current language with whether the fan has read it, for the fan's notification center.

## Requirements

### Requirement: List renders the fan's newest notifications

List SHALL read the fan's Notifications with Notification.ListByUser with the limit 50, read the records each one's subject names and the fan's follows, and return each Notification, newest first, with its message rendered as the Notification entity defines it in the fan's current preferred language, its create time and its read time when it has one. A Notification SHALL be listed whether or not its push reached a browser. A Notification a record of whose subject no longer exists SHALL be left out. When a read fails otherwise, List SHALL fail with that error.

#### Scenario: Failed push still listed
- **WHEN** a fan with no registered browser was sent a lottery_loss Notification
- **THEN** List returns it with its rendered title and body

#### Scenario: Language changed since the push
- **WHEN** a Notification was pushed in Japanese and the fan's preferred language is now `en`
- **THEN** List returns it rendered in English

#### Scenario: Read and unread
- **WHEN** a fan has two Notifications and has read one
- **THEN** List returns both, the read one with its read time and the other without one

#### Scenario: Subject deleted
- **WHEN** the Order a concert_cancelled Notification names no longer exists
- **THEN** List leaves that Notification out and returns the others

#### Scenario: No notification
- **WHEN** the fan has no Notification
- **THEN** List returns an empty list
