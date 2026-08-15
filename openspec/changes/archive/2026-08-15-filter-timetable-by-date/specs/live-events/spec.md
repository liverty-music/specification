## MODIFIED Requirements

### Requirement: Live Schedule Access

The system MUST provide access to the collected schedule of concerts.

#### Scenario: List Concerts

- **WHEN** `ListConcerts` is called for a valid artist ID
- **THEN** the system MUST return a chronologically sorted list of future concerts for that artist.

#### Scenario: List Concerts by Follower

- **WHEN** `ListByFollower` is called by an authenticated user
- **THEN** the system MUST return concerts for all artists followed by that user, grouped by date and classified into home/nearby/away lanes
- **AND** by default (no `from` provided) the result SHALL include only concerts whose local event date is on or after the current date
- **AND** each group SHALL contain a calendar date and three concert lists (home, nearby, away)
- **AND** groups SHALL be ordered by date ascending
- **AND** lane classification SHALL be performed by the backend using the proximity classification model
- **AND** the result SHALL be retrieved in a single RPC call

#### Scenario: List Concerts by Follower from a given date

- **WHEN** `ListByFollower` is called with a `from` date
- **THEN** the system SHALL return concerts for the user's followed artists whose local event date is on or after `from`, including dates in the past when `from` is before the current date
- **AND** the grouping, lane classification, and date-ascending ordering SHALL be identical to the default call

#### Scenario: List Concerts by Follower with no matching concerts

- **WHEN** `ListByFollower` is called and no followed-artist concert falls on or after the effective start date
- **THEN** the system SHALL return an empty list of groups (not an error)
