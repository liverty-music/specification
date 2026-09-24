# SearchLog.Upsert

## Purpose

Starts a new search record for an Artist: sets its search time to now and its status to the given one.

## Requirements

### Requirement: Create or restart the log

Upsert SHALL create the Artist's SearchLog when there is none and otherwise update it, in both cases setting the search time to the current time and the status to the given status, and keeping any last found time.

#### Scenario: First search
- **WHEN** the Artist has no SearchLog and pending is given
- **THEN** a pending SearchLog with the current search time exists

#### Scenario: Restart keeps last found time
- **WHEN** the Artist's SearchLog has a last found time and is upserted as pending
- **THEN** its search time is now, its status pending, and its last found time unchanged
