# Spec Delta

## MODIFIED Requirements

### Requirement: Create or restart the log

Upsert SHALL create the Artist's ConcertSearch when there is none and otherwise update it, in both cases setting the search time to the current time and the status to the given status, and keeping any last find time.

#### Scenario: First search
- **WHEN** the Artist has no ConcertSearch and pending is given
- **THEN** a pending ConcertSearch with the current search time exists

#### Scenario: Restart keeps last find time
- **WHEN** the Artist's ConcertSearch has a last find time and is upserted as pending
- **THEN** its search time is now, its status pending, and its last find time unchanged
