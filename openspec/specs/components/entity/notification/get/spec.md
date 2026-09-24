# Notification.Get

## Purpose

Returns one Notification by its id, whoever it belongs to.

## Requirements

### Requirement: Get returns the notification or NotFound

Get SHALL return the Notification with the given id, with all its attributes. When no Notification has that id, Get SHALL fail with NotFound.

#### Scenario: Existing notification

- **WHEN** Get runs for a stored Notification's id
- **THEN** that Notification is returned, including its owner, delivery status and read and dismiss times

#### Scenario: Unknown id

- **WHEN** no Notification has the given id
- **THEN** Get fails with NotFound
