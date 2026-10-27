## ADDED Requirements

### Requirement: Paid records and purchases in progress block the delete

DeleteAndSuppress SHALL fail with FailedPrecondition, removing nothing and suppressing nothing, when the Event has:
- an Order that is Paid;
- a Settlement that is not Reversed;
- a purchase in progress: a Checkout that is Held or Committed, an Expired or Released Checkout whose card authorization is not yet released, an Entered lottery entry, or a Won lottery entry whose Order is not yet issued.

A purchase started while DeleteAndSuppress runs SHALL either be seen by this check or be refused; it SHALL NOT be removed.

#### Scenario: Concert with issued tickets
- **WHEN** an Event with an issued Ticket of a Paid Order is deleted
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a held settlement
- **WHEN** an Event whose Orders are Refunded has a Held Settlement
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a checkout in progress
- **WHEN** an Event has a Held Checkout
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with an open lottery entry
- **WHEN** an Event has an Entered lottery entry
- **THEN** the call fails with FailedPrecondition and the Event remains

#### Scenario: Concert with a won entry awaiting its order
- **WHEN** an Event has a Won lottery entry whose payment is captured and whose Order is not yet issued
- **THEN** the call fails with FailedPrecondition and the Event and the entry remain

## REMOVED Requirements

### Requirement: Paid records block the delete
**Reason**: A Draft lottery entry no longer exists.
**Migration**: Replaced by "Paid records and purchases in progress block the delete"; the schema migration deletes the Draft entries.
