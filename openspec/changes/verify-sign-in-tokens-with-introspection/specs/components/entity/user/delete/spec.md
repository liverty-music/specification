# Spec Delta

## MODIFIED Requirements

### Requirement: Delete removes the user and what it owns

Delete SHALL remove the User with the given id, including its full name and phone number, together with its follows, ticket journeys, push subscriptions, notifications, ticket sale reminder records and IdentityVerification records. The User's orders, tickets and lottery entries SHALL remain. It SHALL record the User's provider user ID as removed together with the removal: both happen or neither does, and User.Create refuses that provider user ID until User.ForgetRemovedIdentity removes the record. It SHALL fail with NotFound when no User has that id, and with InvalidArgument when the id is empty. It SHALL fail with Unavailable, removing nothing or leaving the removal complete, when the store cannot be reached.

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

#### Scenario: Reminder records go with the user

- **WHEN** Delete runs for a User who was sent a ticket sale reminder
- **THEN** that reminder record no longer exists

#### Scenario: Store unreachable

- **WHEN** the store cannot be reached
- **THEN** Delete fails with Unavailable

#### Scenario: Identity recorded as removed

- **WHEN** Delete runs for a User with provider user ID `abc`
- **THEN** a later User.Create for provider user ID `abc` fails with FailedPrecondition
