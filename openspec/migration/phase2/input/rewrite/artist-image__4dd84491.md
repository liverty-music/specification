<!-- spec: artist-image | target: components/usecase/artist/sync-artist-image | flags: CLASSNAME | new_name: Periodic sync refreshes stale artist images -->

### Requirement: Periodic Image Sync CronJob
The system SHALL run a daily CronJob (`artist-image-sync`) that refreshes stale fanart data and backfills artists without fanart data. The job SHALL select artists where `fanart IS NULL` (prioritized) or `fanart_synced_at` is older than 7 days. The job SHALL use a circuit breaker pattern (stop after 3 consecutive failures).

#### Scenario: Backfill artist without fanart
- **WHEN** the CronJob runs and finds artists with `fanart IS NULL`
- **THEN** it SHALL fetch fanart data for each and persist the result

#### Scenario: Refresh stale fanart
- **WHEN** the CronJob runs and finds artists with `fanart_synced_at` older than 7 days
- **THEN** it SHALL re-fetch fanart data and overwrite the existing JSONB

#### Scenario: Circuit breaker activation
- **WHEN** 3 consecutive fanart.tv API calls fail
- **THEN** the job SHALL stop processing remaining artists and exit with code 0

#### Scenario: SIGTERM during processing
- **WHEN** the job receives SIGTERM while processing
- **THEN** the job SHALL stop processing and exit gracefully
