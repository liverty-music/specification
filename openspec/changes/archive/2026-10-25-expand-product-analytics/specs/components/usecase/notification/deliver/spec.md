## MODIFIED Requirements

### Requirement: The pushed message carries the notification id

Before sending, Deliver SHALL add the recorded Notification's id and its type to the message's data, keeping the rest of the message unchanged, and send that same message to each of the fan's browsers.

#### Scenario: Message identifies its notification

- **WHEN** a Notification is recorded with a new id
- **THEN** the message pushed to every browser of the fan carries that id

#### Scenario: Message names its type

- **WHEN** Deliver records a Notification of type sales_reminder
- **THEN** the message pushed to every browser of the fan carries the type sales_reminder
