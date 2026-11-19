# Delete

## Purpose

Delete lets an admin permanently remove a Concert from the catalog, used to clean up test data. Nothing is recorded about the removed Concert's Venue, date or start time, so a Concert can be created at that slot again.

## Requirements

### Requirement: Delete removes the concert

Delete SHALL remove the Concert with its records (Concert.Delete), whatever the Concert's origin — discovered, approved or Organizer-published — and whatever its performers. Delete SHALL fail with InvalidArgument when no Event id is given, and SHALL return the FailedPrecondition of Concert.Delete unchanged.

#### Scenario: Concert deleted
- **WHEN** an admin deletes a Concert of a test Artist
- **THEN** it is removed and nothing is recorded about its Venue, date or start time

#### Scenario: Missing id
- **WHEN** Delete is called with no Event id
- **THEN** it fails with InvalidArgument and nothing is removed

#### Scenario: Unknown id
- **WHEN** Delete is called with an id that no longer exists
- **THEN** it succeeds and nothing changes

#### Scenario: Concert with issued tickets
- **WHEN** the Concert has an issued Ticket of a Paid Order
- **THEN** Delete fails with FailedPrecondition and nothing is removed

#### Scenario: Cancelled concert after refunds
- **WHEN** an admin deletes a CANCELLED Organizer Concert whose every Order is Refunded
- **THEN** it is removed with its purchases
