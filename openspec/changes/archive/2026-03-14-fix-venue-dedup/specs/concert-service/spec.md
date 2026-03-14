## MODIFIED Requirements

### Requirement: Event Natural Key Constraint

The `events` table SHALL have a composite UNIQUE constraint on the natural key `(artist_id, local_event_date, start_at)` to prevent duplicate event rows at the database level. The `artist_id` column SHALL be added to the `events` table to enable per-artist deduplication independent of venue.

#### Scenario: Duplicate event insert is rejected

- **WHEN** a concert is inserted with the same `(artist_id, local_event_date, start_at)` as an existing event
- **THEN** the database SHALL reject the insert via the UNIQUE constraint
- **AND** the application SHALL handle this gracefully via UPSERT (not error)

#### Scenario: NULL-safe equality for start_at in constraint

- **WHEN** two events have the same `artist_id` and `local_event_date`
- **AND** both have `start_at = NULL`
- **THEN** the UNIQUE constraint SHALL treat them as duplicates
- **AND** the constraint SHALL use a `UNIQUE NULLS NOT DISTINCT` clause

#### Scenario: Same artist and date with different start_at

- **WHEN** two events have the same `artist_id` and `local_event_date`
- **AND** different non-NULL `start_at` values
- **THEN** the UNIQUE constraint SHALL allow both rows (matinee/evening shows)

#### Scenario: Different artists at same venue, date, and time

- **WHEN** two events have different `artist_id` values
- **AND** the same `venue_id`, `local_event_date`, and `start_at`
- **THEN** the UNIQUE constraint SHALL allow both rows (festival/multi-artist events)

### Requirement: Concert UPSERT on Natural Key

The `ConcertRepository.Create` bulk insert SHALL use `ON CONFLICT` on the natural key `(artist_id, local_event_date, start_at)` to perform an UPSERT. The `artist_id` SHALL be included in the events insert as it is now part of the natural key. When a conflict is detected, the existing record's `open_at` SHALL be updated if the new value provides previously unknown information.

#### Scenario: Insert new event (no conflict)

- **WHEN** `Create` is called with a concert whose natural key does not exist
- **THEN** the event SHALL be inserted normally

#### Scenario: Different start_at inserts new row (not UPSERT)

- **WHEN** `Create` is called with a concert at the same `(artist_id, local_event_date)` as an existing event
- **AND** the `start_at` values differ
- **THEN** the natural keys are distinct and no conflict occurs
- **AND** the new concert SHALL be inserted as a separate event row

#### Scenario: Conflict with richer open_at — update existing

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event has `open_at = NULL`
- **AND** the new concert has a non-NULL `open_at`
- **THEN** the existing event's `open_at` SHALL be updated to the new value via `COALESCE(EXCLUDED.open_at, events.open_at)`

#### Scenario: Conflict does not overwrite existing non-NULL open_at with NULL

- **WHEN** `Create` is called with a concert whose natural key matches an existing event
- **AND** the existing event already has a non-NULL `open_at`
- **AND** the new concert has `open_at = NULL`
- **THEN** the existing event's `open_at` SHALL NOT be overwritten

#### Scenario: Concerts row skipped for UPSERTed events with different UUID

- **WHEN** `Create` is called with a concert whose event UUID differs from the existing event at the same natural key
- **THEN** the events UPSERT SHALL update the existing row (keeping the original UUID)
- **AND** the input UUID SHALL NOT exist in the `events` table
- **AND** the `concerts` INSERT SHALL skip this row via `WHERE EXISTS`

### Requirement: Concert Persistence

The system SHALL automatically persist any new concerts discovered via the search mechanism. The `ConcertRepository.Create` method SHALL accept a variadic number of concerts for bulk insert support. The bulk insert SHALL use the PostgreSQL `unnest` pattern instead of manual placeholder construction.

#### Scenario: Persist New Concerts

- **WHEN** `SearchNewConcerts` is called and finds concerts not currently in the database
- **THEN** the new concerts are saved to the persisted storage via a single bulk insert call
- **AND** returned in the response with valid IDs

#### Scenario: Persist Venues

- **WHEN** a discovered concert has a venue that does not exist in the database
- **THEN** a new venue is created dynamically, resolved via Google Places API when available
- **AND** if Google Places API returns a result, the venue SHALL be created with `google_place_id`, canonical name, coordinates, and `enrichment_status = 'enriched'`
- **AND** if Google Places API is unavailable or returns no result, the venue SHALL be created based on the listed venue name with `enrichment_status = 'pending'`
- **AND** the new concert is associated with this venue

#### Scenario: Bulk insert uses unnest

- **WHEN** `Create` is called with multiple concerts
- **THEN** the repository SHALL use `unnest` arrays for both `events` and `concerts` table inserts
- **AND** the events insert SHALL include `artist_id` as part of the unnest arrays
- **AND** the implementation SHALL NOT use manual `fmt.Sprintf` placeholder construction

#### Scenario: Single concert creation

- **WHEN** `Create` is called with a single concert argument
- **THEN** it SHALL behave identically to bulk insert with a single element

### Requirement: Duplicate Data Cleanup Migration

A one-time database migration SHALL delete all existing concert, event, and venue records to ensure a clean state before applying the new natural key constraint.

#### Scenario: All concerts, events, and venues are deleted

- **WHEN** the migration runs
- **THEN** all rows in the `concerts` table SHALL be deleted
- **AND** all rows in the `events` table SHALL be deleted
- **AND** all rows in the `venues` table SHALL be deleted

#### Scenario: artist_id column added to events

- **WHEN** the migration runs
- **THEN** an `artist_id` column of type `UUID NOT NULL` SHALL be added to the `events` table
- **AND** a foreign key constraint referencing `artists(id)` SHALL be added

#### Scenario: New unique constraint applied after cleanup

- **WHEN** the migration runs
- **THEN** the old constraint `uq_events_natural_key` on `(venue_id, local_event_date, start_at)` SHALL be dropped
- **AND** a new constraint `UNIQUE NULLS NOT DISTINCT (artist_id, local_event_date, start_at)` SHALL be added

#### Scenario: Migration is idempotent

- **WHEN** the migration is run on a database with no data
- **THEN** the DELETE statements SHALL complete without error
- **AND** the constraint changes SHALL succeed
