## MODIFIED Requirements

### Requirement: Live Schedule Access

The system MUST provide access to the collected schedule of concerts.

#### Scenario: List Concerts

- **WHEN** `ListConcerts` is called for a valid artist ID
- **THEN** the system MUST return a chronologically sorted list of future concerts for that artist.

#### Scenario: List Concerts by Follower

- **WHEN** `ListByFollower` is called by an authenticated user
- **THEN** the system MUST return a chronologically sorted list of concerts for all artists followed by that user
- **AND** the result SHALL be retrieved in a single RPC call
