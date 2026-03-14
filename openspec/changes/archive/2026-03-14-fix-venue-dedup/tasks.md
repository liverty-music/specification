## 1. Database Migration

- [x] 1.1 Create migration: DELETE all rows from `concerts`, `events`, `venues` tables
- [x] 1.2 Create migration: Add `artist_id UUID NOT NULL` column to `events` table with FK to `artists(id)`
- [x] 1.3 Create migration: Drop old constraint `uq_events_natural_key` on `(venue_id, local_event_date, start_at)`
- [x] 1.4 Create migration: Add new constraint `UNIQUE NULLS NOT DISTINCT (artist_id, local_event_date, start_at)` on `events`
- [x] 1.5 Update `schema.sql` desired state to reflect new `events` table structure
- [x] 1.6 Run `atlas migrate validate --env local` and verify migration integrity

## 2. Venue Repository — `GetByPlaceID`

- [x] 2.1 Add `GetByPlaceID(ctx, placeID string) (*Venue, error)` to `VenueRepository` interface in `entity/venue.go`
- [x] 2.2 Implement `GetByPlaceID` in `rdb/venue_repo.go` (`WHERE google_place_id = $1`)
- [x] 2.3 Add integration test for `GetByPlaceID`

## 3. Venue Resolution — Synchronous Google Places Lookup

- [x] 3.1 Add `PlaceSearcher` dependency to `ConcertCreationUseCase` (reuse existing `venue.PlaceSearcher` interface)
- [x] 3.2 Add `VenueRepository` (with `GetByPlaceID`) dependency to `ConcertCreationUseCase`
- [x] 3.3 Rewrite `resolveVenue` to call Google Places API first, then lookup by `place_id`, falling back to `GetByName` on failure/not-found
- [x] 3.4 Update batch-local cache key from venue name to `place_id` (with fallback to name for non-Places-resolved venues)
- [x] 3.5 When creating a venue from Places API result, set `google_place_id`, canonical name, coordinates, and `enrichment_status = 'enriched'`
- [x] 3.6 Update DI wiring in `internal/di/` to inject `PlaceSearcher` into `ConcertCreationUseCase`

## 4. Concert Dedup Key Change

- [x] 4.1 Rename `DateVenueKey()` to `DateKey()` in `entity/concert.go` — return `date` only (no venue)
- [x] 4.2 Update `DedupeKey()` in `entity/concert.go` — return `date|start_at_utc` (no venue)
- [x] 4.3 Update `executeSearch` dedup logic in `concert_uc.go` to use new key functions (remove venue from `seen`/`seenDate` maps)
- [x] 4.4 Remove the `ListedVenueName == nil` skip in existing concert dedup — all concerts now participate
- [x] 4.5 Update unit tests for `DateKey()` and `DedupeKey()`
- [x] 4.6 Update unit tests for `executeSearch` dedup logic

## 5. Concert Repository — UPSERT with artist_id

- [x] 5.1 Update `upsertEventsQuery` to include `artist_id` in INSERT columns and `unnest` arrays
- [x] 5.2 Update `ON CONFLICT` clause to reference new constraint `(artist_id, local_event_date, start_at)`
- [x] 5.3 Update `ConcertRepository.Create` to pass `artist_id` for each event in the unnest arrays
- [x] 5.4 Update `listConcertsByArtistQuery` and related queries to include `events.artist_id` if needed
- [x] 5.5 Update integration tests for concert repository

## 6. Verification

- [x] 6.1 Run `make check` in backend (lint + tests)
- [x] 6.2 Run `atlas migrate diff --env local` to verify schema.sql matches migrations
