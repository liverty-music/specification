## MODIFIED Requirements

### Requirement: Status only

UpdateStatus SHALL set the status of the Artist's ConcertSearch whose search time is the one given, and change nothing else. When the Artist has no ConcertSearch, or its ConcertSearch has another search time because a later search replaced it, UpdateStatus SHALL change nothing and succeed. The comparison and the write SHALL be one operation, so a search recorded at the same moment is never ended by an earlier one.

#### Scenario: Completed
- **WHEN** a pending ConcertSearch is updated to completed for its search time
- **THEN** its status is completed and its search time unchanged

#### Scenario: No log
- **WHEN** the Artist has no ConcertSearch
- **THEN** UpdateStatus succeeds and nothing is stored

#### Scenario: Replaced search
- **WHEN** a later search has been recorded for the Artist and UpdateStatus is called for the earlier search time
- **THEN** UpdateStatus succeeds and the later ConcertSearch stays pending
