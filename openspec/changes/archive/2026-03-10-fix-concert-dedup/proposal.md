## Why

`SearchNewConcerts` fails to deduplicate concerts across repeated CronJob runs, causing the same real-world concert to be stored hundreds of times with different `event_id` values. The root cause is that `getUniqueKey(date, startTime)` compares `startTime` as an RFC3339 string — timezone differences between Gemini API responses (e.g., `+09:00`) and pgx DB readback (always UTC) produce different strings for the same instant, bypassing dedup on every run. Additionally, the key does not include the venue name, so distinct concerts at different venues on the same date are incorrectly collapsed, while same-venue concerts with `startTime` fluctuations pass through as "new". In production, 97,041 event rows exist for only 484 unique concerts (200× bloat across 41 artists).

## What Changes

- Replace the dedup key from `(local_event_date, start_at_rfc3339)` to `(local_event_date, listed_venue_name, start_at_utc)` with explicit nil-handling rules for `start_at`.
- Add a DB-level UNIQUE constraint on the `events` table as a final safety net against duplicate inserts.
- Change the INSERT strategy from `ON CONFLICT (event_id) DO NOTHING` to an UPSERT on the natural key, allowing `start_at` / `open_at` updates when new information is discovered.
- Provide a one-time data cleanup migration to deduplicate the 97,041 existing rows down to 484.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-search`: Add a new requirement defining the dedup natural key, start_at comparison semantics, and nil-handling rules for the dedup logic in `executeSearch`.
- `concert-service`: Add a new requirement defining the DB-level natural key constraint and UPSERT behavior in `ConcertRepository.Create`.

## Impact

- **Backend**: `internal/usecase/concert_uc.go` (dedup logic), `internal/infrastructure/database/rdb/concert_repo.go` (INSERT → UPSERT), `internal/infrastructure/database/rdb/schema/schema.sql` (UNIQUE constraint).
- **Database**: New migration to add UNIQUE constraint and clean up existing duplicates. Migration must run before the new code deploys.
- **Frontend**: No changes — the API contract is unchanged; the frontend will simply stop receiving duplicate rows.
