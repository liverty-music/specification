## 1. Fix Application-Level Dedup Logic

- [x] 1.1 Replace `getUniqueKey(date, startTime)` with new function that uses `(local_event_date, listed_venue_name, start_at_utc)` with nil-handling rules per design
- [x] 1.2 Update `executeSearch` dedup loop to use dual lookup sets (`seen` for full key, `seenDateVenue` for nil-match) per design Decision 2
- [x] 1.3 Verify all 9 `TestSearchNewConcerts_Deduplication` test cases pass (5 currently failing)

## 2. Database Migration — Cleanup and Constraint

- [x] 2.1 Write cleanup SQL to delete duplicate events, keeping the richest/earliest row per `(venue_id, local_event_date, start_at)` natural key
- [x] 2.2 Add `UNIQUE NULLS NOT DISTINCT (venue_id, local_event_date, start_at)` constraint on `events` table
- [x] 2.3 Generate Atlas migration: `atlas migrate diff --env local fix_concert_dedup`
- [x] 2.4 Update `schema.sql` with the new UNIQUE constraint
- [x] 2.5 Add migration file to `k8s/atlas/base/kustomization.yaml`

## 3. UPSERT in ConcertRepository

- [x] 3.1 Change `insertEventsUnnestQuery` from `ON CONFLICT DO NOTHING` to `ON CONFLICT (venue_id, local_event_date, start_at) DO UPDATE SET start_at = COALESCE(EXCLUDED.start_at, events.start_at), open_at = COALESCE(EXCLUDED.open_at, events.open_at)`
- [x] 3.2 Verify `insertConcertsUnnestQuery` handles the case where the event already exists (the `concerts` row may also already exist)

## 4. Verification

- [x] 4.1 Run `make check` (lint + full test suite)
- [x] 4.2 Apply migration locally and verify duplicate cleanup reduces row count

## 5. Dev DB Cleanup

- [x] 5.1 Delete all concert-related data from dev DB (TRUNCATE concerts, events, search_logs CASCADE) to remove duplicated rows and allow clean re-discovery
