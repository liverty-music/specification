# ConcertSearch.MarkFound

## Purpose

Records that a search for an Artist found at least one new concert.

## Requirements

### Requirement: Last find time set to now

MarkFound SHALL set the last find time of the Artist's ConcertSearch to the current time; when the Artist has no ConcertSearch it SHALL change nothing and succeed.

#### Scenario: Found
- **WHEN** MarkFound is called for an Artist with a ConcertSearch
- **THEN** its last find time is the current time
