# User.Delete

## Purpose

Removes a User together with everything that belongs only to that User.

## Requirements

### Requirement: Delete removes the user and what it owns

Delete SHALL remove the User with the given id together with its follows, ticket journeys, push subscriptions, notifications, sales-phase reminder records and verified identities. The User's orders, tickets and ticket applications SHALL remain. It SHALL fail with NotFound when no User has that id, and with InvalidArgument when the id is empty.

#### Scenario: Existing user

- **WHEN** Delete runs for a stored User who follows an artist
- **THEN** the User and that follow no longer exist

#### Scenario: Purchases outlive the user

- **WHEN** Delete runs for a User who holds a ticket
- **THEN** the ticket and its order remain

#### Scenario: Unknown id

- **WHEN** no User has the given id
- **THEN** Delete fails with NotFound

#### Scenario: Empty id

- **WHEN** the id is empty
- **THEN** Delete fails with InvalidArgument
