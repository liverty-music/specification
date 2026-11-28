## Purpose

Lists the registered artists in one mbid_status, so the artists still to verify, or waiting for an admin's choice, can be worked through.

## ADDED Requirements

### Requirement: ListByMBIDStatus returns the artists in that status, oldest first
ListByMBIDStatus SHALL return every registered artist whose mbid_status is the given status, in the order the artists were registered, oldest first. When no artist is in that status, it SHALL return an empty list.

#### Scenario: Ambiguous artists
- **WHEN** ListByMBIDStatus is called with Ambiguous and two of three artists are Ambiguous
- **THEN** it returns those two, the one registered first listed first

#### Scenario: No artist in the status
- **WHEN** no artist is Unverified and ListByMBIDStatus is called with Unverified
- **THEN** it returns an empty list
