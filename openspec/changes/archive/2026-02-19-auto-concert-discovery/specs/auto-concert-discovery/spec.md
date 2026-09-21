## ADDED Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist sequentially

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

### Requirement: Circuit Breaker on Consecutive Failures

The job SHALL stop processing further artists after 3 consecutive errors from `SearchNewConcerts`, treating this as a systemic failure indicator.

#### Scenario: 3 consecutive errors triggers stop

- **WHEN** `SearchNewConcerts` returns an error for 3 consecutive artists
- **THEN** the job SHALL log a warning indicating circuit break activation
- **AND** stop processing remaining artists
- **AND** exit with status code 0

#### Scenario: Successful search resets error counter

- **WHEN** `SearchNewConcerts` succeeds after 1 or 2 consecutive errors
- **THEN** the consecutive error counter SHALL reset to 0
- **AND** processing continues normally

#### Scenario: Individual artist failure is non-fatal

- **WHEN** `SearchNewConcerts` returns an error for a single artist (fewer than 3 consecutive)
- **THEN** the job SHALL log the error with the artist ID
- **AND** continue processing the next artist

