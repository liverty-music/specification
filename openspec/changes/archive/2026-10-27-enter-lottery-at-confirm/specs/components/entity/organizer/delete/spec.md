## ADDED Requirements

### Requirement: Delete refuses while purchases or payouts remain

Delete SHALL fail with FailedPrecondition and remove nothing when, at the moment it runs:

- the Organizer is not deactivated;
- any of its Events has an Order that is Paid;
- any of its Events has a Settlement that is not Reversed;
- any of its Events has a purchase in progress: a Checkout that is Held or Committed, an Expired or Released Checkout whose card authorization is not yet released, an Entered lottery entry, or a Won lottery entry whose Order is not yet issued;
- the Organizer has a payout-account record.

A purchase started while Delete runs SHALL either be seen by these checks or be refused; it SHALL NOT be removed.

#### Scenario: Active Organizer

- **WHEN** Delete runs for an active Organizer
- **THEN** it fails with FailedPrecondition and the Organizer and its Series remain

#### Scenario: Paid order

- **WHEN** an Event of the Organizer has a Paid Order
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Settlement

- **WHEN** an Event of the Organizer has a Held or Released Settlement
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Purchase in progress

- **WHEN** an Event of the Organizer has an Entered lottery entry
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Won entry awaiting its order

- **WHEN** an Event of the Organizer has a Won lottery entry whose Order is not yet issued
- **THEN** it fails with FailedPrecondition and nothing is removed

#### Scenario: Payout account

- **WHEN** the Organizer has a payout-account record
- **THEN** it fails with FailedPrecondition and nothing is removed

## REMOVED Requirements

### Requirement: Delete refuses when deletion is blocked
**Reason**: A Draft lottery entry no longer exists.
**Migration**: Replaced by "Delete refuses while purchases or payouts remain"; the schema migration deletes the Draft entries.
