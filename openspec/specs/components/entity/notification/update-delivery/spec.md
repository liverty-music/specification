# Notification.UpdateDelivery

## Purpose

Records the outcome of a Notification's push: Delivered with the time the push channel accepted it, or Failed with the reason.

## Requirements

### Requirement: UpdateDelivery stores the outcome and keeps the record

UpdateDelivery SHALL set the Notification's delivery status to the given outcome: Delivered with its deliver time and no failure reason, or Failed with its failure reason. The Notification SHALL never be removed by it. When no Notification has the given id, UpdateDelivery SHALL succeed and change nothing.

#### Scenario: Delivered

- **WHEN** UpdateDelivery runs with Delivered and a time
- **THEN** the Notification is Delivered with that deliver time

#### Scenario: Failed

- **WHEN** UpdateDelivery runs with Failed and the reason "no active push subscription"
- **THEN** the Notification is Failed with that reason and is still stored

#### Scenario: Unknown id

- **WHEN** no Notification has the given id
- **THEN** UpdateDelivery succeeds and nothing changes
