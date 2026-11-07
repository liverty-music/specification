## Purpose

The notification center (`/notifications`) lists every notification sent to the signed-in fan, newest first, whether or not its push reached a browser, and lets the fan open each one.

## ADDED Requirements

### Requirement: The center lists the fan's newest notifications

The notification center SHALL list the signed-in fan's notifications as NotificationUseCase.List returns them, at most 50, newest first. Each item SHALL show its title, its body with line breaks kept, and when it was sent, relative to now for the last 24 hours (for example 2時間前 / 2 hours ago) and as month/day before that. An unread item SHALL be marked as unread; a read item SHALL be shown dimmed. With no notification, the center SHALL say there is no notification yet. When the list cannot be loaded, the center SHALL show the error and a way to try again.

#### Scenario: Notifications listed
- **WHEN** a fan with three notifications, one of them read, opens the center
- **THEN** three items are shown newest first, two marked unread and one dimmed

#### Scenario: Push never reached the fan
- **WHEN** a fan who never allowed push notifications opens the center after a lottery_loss notification was sent
- **THEN** that notification is listed

#### Scenario: Empty
- **WHEN** a fan with no notification opens the center
- **THEN** the center says there is no notification yet

### Requirement: Tapping an item marks it read and opens its link

Tapping an item SHALL mark its Notification read (NotificationUseCase.MarkRead) and open its link. A failure to mark it read SHALL NOT stop the link from opening.

#### Scenario: Tap an unread item
- **WHEN** a fan taps an unread lottery_win item
- **THEN** the Tickets screen opens and the item is read when the fan comes back to the center

### Requirement: Only a signed-in fan can open the center

The center SHALL be a protected route: a guest who opens `/notifications` SHALL be sent to the welcome page with a notice, as the app shell's auth guard does for every protected route.

#### Scenario: Guest
- **WHEN** a guest opens `/notifications`
- **THEN** the welcome page opens with a notice and the center is not shown
