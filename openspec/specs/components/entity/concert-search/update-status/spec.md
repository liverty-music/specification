# ConcertSearch.UpdateStatus

## Purpose

Records how an Artist's latest search ended.

## Requirements

### Requirement: Status only

UpdateStatus SHALL set the status of the Artist's ConcertSearch and change nothing else; when the Artist has no ConcertSearch it SHALL change nothing and succeed.

#### Scenario: Completed
- **WHEN** a pending ConcertSearch is updated to completed
- **THEN** its status is completed and its search time unchanged

#### Scenario: No log
- **WHEN** the Artist has no ConcertSearch
- **THEN** UpdateStatus succeeds and nothing is stored
