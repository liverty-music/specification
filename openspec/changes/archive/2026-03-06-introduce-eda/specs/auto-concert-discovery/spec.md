## MODIFIED Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist. The CronJob SHALL be a publish-only loop; notification and venue enrichment are handled by event consumers.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist sequentially
- **AND** `SearchNewConcerts` SHALL publish `concert.discovered.v1` events internally

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

#### Scenario: CronJob does not call NotifyNewConcerts directly

- **WHEN** the CronJob loop completes processing an artist
- **THEN** the CronJob SHALL NOT call `PushNotificationUseCase.NotifyNewConcerts`
- **AND** notifications SHALL be triggered by the `concert.created.v1` event consumer

#### Scenario: CronJob does not call EnrichPendingVenues directly

- **WHEN** the CronJob loop completes all artists
- **THEN** the CronJob SHALL NOT call `VenueEnrichmentUseCase.EnrichPendingVenues`
- **AND** venue enrichment SHALL be triggered by the `venue.created.v1` event consumer

### Requirement: SearchNewConcerts as Search-and-Publish

The `SearchNewConcerts` use case SHALL perform external API search, deduplication, and event publishing only. Concert persistence, venue resolution, and notification delivery are handled by downstream event consumers.

#### Scenario: Successful search and publish

- **WHEN** `SearchNewConcerts` is called with a valid artist ID
- **AND** the search log TTL has expired (or no log exists)
- **THEN** the system SHALL call the external search API (Gemini)
- **AND** deduplicate results against existing concerts in the database
- **AND** publish a single `concert.discovered.v1` event containing the artist ID and the batch of new scraped concerts
- **AND** return nil error

#### Scenario: No new concerts found

- **WHEN** the external search returns results
- **AND** all results are duplicates of existing concerts
- **THEN** the system SHALL NOT publish a `concert.discovered.v1` event
- **AND** return nil error

#### Scenario: Search skipped due to TTL

- **WHEN** `SearchNewConcerts` is called
- **AND** the search log indicates the artist was searched within the last 24 hours
- **THEN** the system SHALL NOT call the external API
- **AND** SHALL NOT publish any event
- **AND** return nil error

#### Scenario: External API failure

- **WHEN** the external search API returns an error
- **THEN** the system SHALL delete the search log entry to allow retry
- **AND** return the error to the caller

#### Scenario: Return type change

- **WHEN** `SearchNewConcerts` completes
- **THEN** it SHALL return only `error` (not `[]*entity.Concert, error`)
- **AND** the caller SHALL NOT depend on a list of discovered concerts

### Requirement: Job-Specific Dependency Injection

The CronJob SHALL use a lightweight DI initializer that provisions only the dependencies required for batch processing, without starting an HTTP server.

#### Scenario: Job initialization

- **WHEN** the concert discovery job starts
- **THEN** it SHALL initialize config, logger, database, repositories, Gemini searcher, ConcertUseCase, and a Watermill Publisher
- **AND** it SHALL NOT initialize PushNotificationUseCase, VenueEnrichmentUseCase, HTTP server, RPC handlers, auth interceptors, or in-memory caches

#### Scenario: Graceful resource cleanup

- **WHEN** the job completes (success or circuit break)
- **THEN** it SHALL close all initialized resources (database connections, NATS publisher, telemetry)
