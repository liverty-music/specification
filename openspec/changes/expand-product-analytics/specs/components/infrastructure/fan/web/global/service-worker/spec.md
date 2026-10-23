## ADDED Requirements

### Requirement: Notification interactions name the notification's type

The usage analytics event the Service Worker sends when a fan opens or dismisses a push notification SHALL carry, besides the notification id, the notification's type and, for a sales reminder, its milestone, as the pushed message's data states them, and the path of the screen the notification opens. A message whose data lacks the type SHALL still be reported, without it.

#### Scenario: Opened sales reminder
- **WHEN** a fan opens a sales reminder for the apply-open milestone of a sale
- **THEN** the opened event carries type sales_reminder, the apply-open milestone and the path of the event it opens

#### Scenario: Older message without a type
- **WHEN** a fan dismisses a notification whose data carries only its id and link
- **THEN** the dismissed event is sent with the notification id and the path, and no type
