# Delete

## Purpose

Delete lets an admin permanently remove a Concert from the catalog and suppress its slot, so that neither discovery nor organizer publishing brings it back.

## Requirements

### Requirement: Delete removes and suppresses

Delete SHALL remove the Concert and suppress its slot (Concert.DeleteAndSuppress), whatever the Concert's origin — discovered, approved or organizer-published — and whatever its performers. Delete SHALL fail with InvalidArgument when no Event id is given.

#### Scenario: Auto-published concert deleted
- **WHEN** an admin deletes a discovered Concert
- **THEN** it is removed and its Venue, date and start time are suppressed

#### Scenario: Missing id
- **WHEN** Delete is called with no Event id
- **THEN** it fails with InvalidArgument and nothing is removed

#### Scenario: Unknown id
- **WHEN** Delete is called with an id that no longer exists
- **THEN** it succeeds and nothing is suppressed

#### Scenario: Concert with issued tickets
- **WHEN** the Concert has an issued Ticket
- **THEN** Delete fails with FailedPrecondition and nothing is removed
