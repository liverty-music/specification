# Notification.Create

## Purpose

Records a new Notification for a fan before anything is sent, assigning its id and queue time.

## Requirements

### Requirement: Create records a Queued notification and assigns its identity

Create SHALL store the Notification as Queued, assign it a new unique id and its queue time, and return both to the caller. When the fan does not exist, Create SHALL fail with FailedPrecondition and store nothing.

#### Scenario: Notification recorded

- **WHEN** Create runs for an existing fan with type new_concerts and a message
- **THEN** a Queued Notification is stored and the caller receives its new id and queue time

#### Scenario: Two notifications

- **WHEN** Create runs twice with the same fan, type and message
- **THEN** two Notifications with different ids are stored

#### Scenario: Unknown fan

- **WHEN** the fan does not exist
- **THEN** Create fails with FailedPrecondition and nothing is stored
