## REMOVED Requirements

### Requirement: Concert calls get 120 seconds, every other call 30 seconds

**Reason**: The longer limit existed for SearchNewConcerts, the only fan call that ran a concert search. That call leaves the fan API, and every remaining concert call is a read.

**Migration**: Concert calls fall under "Every fan call gets 30 seconds" below.

## ADDED Requirements

### Requirement: Every fan call gets 30 seconds

Every call to any service of the fan API SHALL be given up after 30 seconds. A call that is given up SHALL fail with Unavailable, and the caller receives no partial result.

#### Scenario: Concert call over the limit

- **WHEN** a concert call is still running after 30 seconds
- **THEN** the caller receives Unavailable

#### Scenario: Other call over the limit

- **WHEN** a follow call is still running after 30 seconds
- **THEN** the caller receives Unavailable
