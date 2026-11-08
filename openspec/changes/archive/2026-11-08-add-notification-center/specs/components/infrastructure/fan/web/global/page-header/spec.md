## ADDED Requirements

### Requirement: The header shows a notification bell with the unread count

While a fan is signed in, the shell-hosted page header SHALL show a bell that opens the notification center (`/notifications`). The bell SHALL show the number of unread notifications among the 50 the notification center lists, as a badge, and no badge when there is none; the count is refreshed when the app starts, when it returns to the foreground, and after the fan marks a notification read. A guest SHALL see no bell.

#### Scenario: Two unread
- **WHEN** a signed-in fan has two unread notifications among their newest 50
- **THEN** the bell shows the badge 2

#### Scenario: All read
- **WHEN** every listed notification of the fan is read
- **THEN** the bell shows no badge

#### Scenario: Guest
- **WHEN** a guest opens the app
- **THEN** the header shows no bell

#### Scenario: Open the center
- **WHEN** the fan taps the bell
- **THEN** the notification center opens
