# SearchLog.MarkFound

## Purpose

Records that a search for an Artist found at least one new concert.

## Requirements

### Requirement: Last found time set to now

MarkFound SHALL set the last found time of the Artist's SearchLog to the current time; when the Artist has no SearchLog it SHALL change nothing and succeed.

#### Scenario: Found
- **WHEN** MarkFound is called for an Artist with a SearchLog
- **THEN** its last found time is the current time
