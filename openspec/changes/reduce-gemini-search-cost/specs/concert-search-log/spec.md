## ADDED Requirements

### Requirement: Track Last Concert Discovery Time

The system SHALL record, per artist, the timestamp at which a search most recently discovered at least one genuinely new concert. This timestamp drives the discovery-recency skip in concert search and is distinct from `searched_at` (which records every search attempt, productive or not).

#### Scenario: Record discovery when new concerts are published

- **WHEN** a search for an artist produces one or more new concerts after deduplication (i.e. a `concert.discovered` event is published)
- **THEN** the system MUST set the artist's `last_found_at` to the current timestamp in `latest_search_logs`

#### Scenario: Do not record discovery when nothing new is found

- **WHEN** a search for an artist completes but yields no new concerts after deduplication
- **THEN** the system MUST NOT modify the artist's `last_found_at`
- **AND** the existing `last_found_at` value (if any) MUST be preserved

#### Scenario: Never discovered

- **WHEN** an artist has never had a search produce a new concert
- **THEN** the artist's `last_found_at` MUST be null

## MODIFIED Requirements

### Requirement: Search Log Persistence

The system SHALL store search logs in a `latest_search_logs` table with `artist_id` as the primary key, `searched_at` as a non-null timestamp with timezone, and `last_found_at` as a nullable timestamp with timezone recording the most recent successful discovery.

#### Scenario: Schema definition

- **WHEN** the `latest_search_logs` table is queried
- **THEN** it MUST contain columns `artist_id` (PK, FK to `artists.id`), `searched_at` (timestamptz, NOT NULL), and `last_found_at` (timestamptz, NULL)

#### Scenario: Additive nullable column migration

- **WHEN** the migration adding `last_found_at` is applied
- **THEN** existing rows MUST retain their `artist_id` and `searched_at`
- **AND** their `last_found_at` MUST default to null without requiring a backfill
