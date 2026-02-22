## MODIFIED Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist. After discovering new concerts for an artist, the job SHALL dispatch push notifications to that artist's followers.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist sequentially
- **AND** if new concerts are discovered, call `NotifyNewConcerts` for that artist

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

### Requirement: Job-Specific Dependency Injection

The CronJob SHALL use a lightweight DI initializer that provisions only the dependencies required for batch processing, without starting an HTTP server.

#### Scenario: Job initialization

- **WHEN** the concert discovery job starts
- **THEN** it SHALL initialize config, logger, database, repositories, Gemini searcher, ConcertUseCase, and PushNotificationUseCase
- **AND** it SHALL NOT initialize HTTP server, RPC handlers, auth interceptors, or in-memory caches

#### Scenario: Graceful resource cleanup

- **WHEN** the job completes (success or circuit break)
- **THEN** it SHALL close all initialized resources (database connections, telemetry)
