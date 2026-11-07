## MODIFIED Requirements

### Requirement: Create records a Queued notification and assigns its identity

Create SHALL store the Notification with its fan, type and subject, unread, assign it a new unique id and its create time, and return both to the caller. When the fan does not exist, Create SHALL fail with FailedPrecondition and store nothing. When the subject is invalid for the type, Create SHALL fail with InvalidArgument and store nothing.

#### Scenario: Notification recorded

- **WHEN** Create runs for an existing fan with type new_concerts, an artist and one concert
- **THEN** an unread Notification is stored and the caller receives its new id and create time

#### Scenario: Two notifications

- **WHEN** Create runs twice with the same fan, type and subject
- **THEN** two Notifications with different ids are stored

#### Scenario: Unknown fan

- **WHEN** the fan does not exist
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Subject missing a record

- **WHEN** Create runs with type lottery_loss and a subject that names no LotteryEntry
- **THEN** Create fails with InvalidArgument and nothing is stored
