## ADDED Requirements

### Requirement: Event Natural Key Constraint

The `events` table SHALL have a composite UNIQUE constraint on the natural key `(venue_id, local_event_date, start_at)` to prevent duplicate event rows at the database level. This constraint serves as the final safety net when application-level dedup fails.

#### Scenario: Duplicate event insert is rejected

- **WHEN** a concert is inserted with the same `(venue_id, local_event_date, start_at)` as an existing event
- **THEN** the database SHALL reject the insert via the UNIQUE constraint
- **AND** the application SHALL handle this gracefully via UPSERT (not error)

#### Scenario: NULL-safe equality for start_at in constraint

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** both have `start_at = NULL`
- **THEN** the UNIQUE constraint SHALL treat them as duplicates
- **AND** the constraint SHALL use a `UNIQUE NULLS NOT DISTINCT` clause or a partial unique index to handle NULL equality

#### Scenario: Same venue and date with different start_at

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** different non-NULL `start_at` values
- **THEN** the UNIQUE constraint SHALL allow both rows (matinee/evening shows)

### Requirement: Concert UPSERT on Natural Key

The `ConcertRepository.Create` bulk insert SHALL use `ON CONFLICT` on the natural key to perform an UPSERT. When a conflict is detected, the existing record's `open_at` SHALL be updated if the new value provides previously unknown information. Since `start_at` is part of the natural key, a conflict implies both rows have the same `start_at` value (including both NULL); therefore `start_at` updates happen via new row insertion, not UPSERT update.

#### Scenario: Insert new event (no conflict)

- **WHEN** `Create` is called with a concert whose natural key does not exist
- **THEN** the event SHALL be inserted normally

#### Scenario: Different start_at inserts new row (not UPSERT)

- **WHEN** `Create` is called with a concert at the same `(venue_id, local_event_date)` as an existing event
- **AND** the `start_at` values differ (e.g., existing is NULL, new is non-NULL; or both are non-NULL but different instants)
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
- **AND** SHALL retain its current value via `COALESCE(NULL, events.open_at)`

#### Scenario: Concerts row skipped for UPSERTed events with different UUID

- **WHEN** `Create` is called with a concert whose event UUID differs from the existing event at the same natural key
- **THEN** the events UPSERT SHALL update the existing row (keeping the original UUID)
- **AND** the input UUID SHALL NOT exist in the `events` table
- **AND** the `concerts` INSERT SHALL skip this row via `WHERE EXISTS` (no duplicate concerts row created)

### Requirement: Duplicate Data Cleanup Migration

A one-time database migration SHALL remove duplicate event rows created by the bug, retaining only the earliest-inserted row per natural key.

#### Scenario: Dedup retains earliest event per natural key

- **WHEN** the migration runs
- **AND** multiple events share the same `(venue_id, local_event_date, start_at)` (NULL-safe)
- **THEN** only the event with the smallest `id` (earliest UUIDv7 timestamp) SHALL be retained
- **AND** all other duplicates SHALL be deleted
- **AND** corresponding `concerts` rows for deleted events SHALL be cascade-deleted

#### Scenario: Migration is idempotent

- **WHEN** the migration is run on a database with no duplicates
- **THEN** no rows SHALL be deleted
- **AND** the migration SHALL complete without error

#### Scenario: UNIQUE constraint applied after cleanup

- **WHEN** the migration runs
- **THEN** it SHALL first delete duplicates
- **AND** then add the UNIQUE constraint
- **AND** the constraint addition SHALL succeed because duplicates have been removed
