# Capability: Concert Search Log

## Purpose

To track when each artist's concerts were last searched via external sources, enabling time-based caching that prevents redundant API calls.

## Requirements

### Requirement: Track Concert Search History

The system SHALL maintain a log of when each artist's concerts were last searched via external sources. The log is keyed by artist ID and records the timestamp of the most recent search.

#### Scenario: Record search after Gemini call

- **WHEN** `SearchNewConcerts` completes a Gemini API call for an artist
- **THEN** the system MUST upsert a record in `latest_search_logs` with the artist's ID and the current timestamp

#### Scenario: First search for an artist

- **WHEN** no search log exists for the given artist
- **THEN** the system MUST insert a new record with the current timestamp

#### Scenario: Subsequent search for an artist

- **WHEN** a search log already exists for the given artist
- **THEN** the system MUST update the existing record's `searched_at` to the current timestamp

### Requirement: Search Log Persistence

The system SHALL store search logs in a `latest_search_logs` table with `artist_id` as the primary key, `searched_at` as a non-null timestamp with timezone, and `last_found_at` as a nullable timestamp with timezone recording the most recent successful discovery.

#### Scenario: Schema definition

- **WHEN** the `latest_search_logs` table is queried
- **THEN** it MUST contain columns `artist_id` (PK, FK to `artists.id`), `searched_at` (timestamptz, NOT NULL), and `last_found_at` (timestamptz, NULL)

#### Scenario: Additive nullable column migration

- **WHEN** the migration adding `last_found_at` is applied
- **THEN** existing rows MUST retain their `artist_id` and `searched_at`
- **AND** their `last_found_at` MUST default to null without requiring a backfill

### Requirement: Frontend search status polling for onboarding

The frontend SHALL poll the `ListSearchStatuses` RPC during onboarding to detect when backend concert searches have actually completed, rather than relying on the `SearchNewConcerts` RPC return (which is fire-and-forget).

#### Scenario: Polling starts after SearchNewConcerts fires

- **WHEN** the frontend calls `SearchNewConcerts` for an artist during onboarding
- **THEN** the system SHALL add the artist ID to the set of pending searches
- **AND** the system SHALL start (or continue) a polling timer if not already running

#### Scenario: Batched polling every 2 seconds

- **WHEN** the polling timer fires
- **AND** there are one or more artist IDs with pending search status
- **THEN** the system SHALL call `ListSearchStatuses` with all pending artist IDs in a single batched request
- **AND** for each artist whose status is `COMPLETED` or `FAILED`, the system SHALL mark that artist's search as done
- **AND** for each artist whose status is `PENDING` or `UNSPECIFIED`, the system SHALL keep it in the pending set for the next poll cycle

#### Scenario: Polling stops when all searches resolve

- **WHEN** all artist IDs in the pending set have reached a terminal state (`COMPLETED`, `FAILED`, or timed out)
- **THEN** the system SHALL clear the polling interval timer
- **AND** the system SHALL trigger concert data verification (`verifyConcertData`)

#### Scenario: Per-artist timeout as polling deadline

- **WHEN** an artist's search has been pending for 15 seconds (measured from the time `SearchNewConcerts` was fired)
- **AND** the artist's status has not yet reached `COMPLETED` or `FAILED`
- **THEN** the system SHALL treat the artist's search as done (timed out)
- **AND** the system SHALL remove the artist from the pending set

#### Scenario: Polling error handling

- **WHEN** a `ListSearchStatuses` poll call fails with a network or RPC error
- **THEN** the system SHALL log the error
- **AND** the system SHALL NOT mark any artists as done
- **AND** the system SHALL retry on the next poll cycle (2 seconds later)
- **AND** the per-artist 15-second timeout SHALL still apply independently of poll errors

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
