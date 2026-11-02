## MODIFIED Requirements

### Requirement: UpdateDelivery stores the outcome and keeps the record

UpdateDelivery SHALL set the delivery status of a Queued Notification to the given outcome: Delivered with its deliver time and no failure reason, or Failed with its failure reason. A Notification that is already Delivered or Failed SHALL be left unchanged, and UpdateDelivery SHALL still succeed. The Notification SHALL never be removed by it. When no Notification has the given id, UpdateDelivery SHALL succeed and change nothing.

#### Scenario: Delivered

- **WHEN** UpdateDelivery runs on a Queued Notification with Delivered and a time
- **THEN** the Notification is Delivered with that deliver time

#### Scenario: Failed

- **WHEN** UpdateDelivery runs on a Queued Notification with Failed and the reason "no active push subscription"
- **THEN** the Notification is Failed with that reason and is still stored

#### Scenario: Outcome already recorded

- **WHEN** UpdateDelivery runs with Delivered on a Notification that is already Delivered at 18:00
- **THEN** UpdateDelivery succeeds and the Notification stays Delivered at 18:00

#### Scenario: Unknown id

- **WHEN** no Notification has the given id
- **THEN** UpdateDelivery succeeds and nothing changes

## ADDED Requirements

### Requirement: A delivered Notification is announced with the change

When UpdateDelivery makes a Notification Delivered, it SHALL announce the Notification as delivered, carrying it with its deliver time, together with the change: both are stored or neither is. When it makes a Notification Failed, or changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, UpdateDelivery SHALL fail with Unavailable and the Notification SHALL stay Queued.

#### Scenario: Delivered announced

- **WHEN** UpdateDelivery makes a Queued Notification Delivered at 18:00
- **THEN** one delivery is announced, carrying the Notification Delivered at 18:00

#### Scenario: Failed

- **WHEN** UpdateDelivery makes a Queued Notification Failed
- **THEN** nothing is announced

#### Scenario: Already Delivered

- **WHEN** UpdateDelivery runs with Delivered on a Notification that is already Delivered
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** UpdateDelivery would make a Queued Notification Delivered and the announcement cannot be recorded
- **THEN** UpdateDelivery fails with Unavailable and the Notification stays Queued
