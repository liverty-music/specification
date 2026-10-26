## MODIFIED Requirements

### Requirement: Delete removes and suppresses

Delete SHALL remove the Concert and suppress its slot (Concert.DeleteAndSuppress), whatever the Concert's origin — discovered, approved or Organizer-published — and whatever its performers. Delete SHALL fail with InvalidArgument when no Event id is given, and SHALL return the FailedPrecondition of Concert.DeleteAndSuppress unchanged.

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
- **WHEN** the Concert has an issued Ticket of a Paid Order
- **THEN** Delete fails with FailedPrecondition and nothing is removed

#### Scenario: Cancelled concert after refunds
- **WHEN** an admin deletes a CANCELLED Organizer Concert whose every Order is Refunded
- **THEN** it is removed with its purchases and its slot is suppressed
