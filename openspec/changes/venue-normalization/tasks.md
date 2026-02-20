## 1. Database Migration

- [ ] 1.1 Create `venue_enrichment_status` ENUM type (`pending`, `enriched`, `failed`) in a new migration file
- [ ] 1.2 Add `mbid TEXT`, `google_place_id TEXT`, `enrichment_status venue_enrichment_status NOT NULL DEFAULT 'pending'`, `raw_name TEXT` columns to `venues` table (backfill `raw_name` from existing `name`: `UPDATE venues SET raw_name = name`)
- [ ] 1.3 Add unique partial indexes: `CREATE UNIQUE INDEX ON venues (mbid) WHERE mbid IS NOT NULL` and `CREATE UNIQUE INDEX ON venues (google_place_id) WHERE google_place_id IS NOT NULL`; add non-unique index: `CREATE INDEX idx_venues_raw_name ON venues (raw_name)`
- [ ] 1.4 Update `schema.sql` to reflect the new columns, enum type, and indexes

## 2. Entity Layer

- [ ] 2.1 Add `MBID string`, `GooglePlaceID string`, `EnrichmentStatus string`, `RawName string` fields to `Venue` in `internal/entity/venue.go`
- [ ] 2.2 Add `VenueEnrichmentStatus` typed constants (`Pending`, `Enriched`, `Failed`) in `internal/entity/venue.go`
- [ ] 2.3 Create `VenueEnrichmentRepository` interface in `internal/entity/venue.go` with `ListPending(ctx) ([]*Venue, error)`, `UpdateEnriched(ctx, venue) error`, `MarkFailed(ctx, id) error`, and `MergeVenues(ctx, canonicalID, duplicateID string) error`

## 3. MusicBrainz Client — Place Endpoint

- [ ] 3.1 Add `SearchPlace(ctx, name, adminArea string) (*Place, error)` method to MusicBrainz client in `internal/infrastructure/music/musicbrainz/client.go`
- [ ] 3.2 Define `Place` response struct with `ID`, `Name` fields
- [ ] 3.3 Add unit test for `SearchPlace` using `httptest` server in `client_test.go`

## 4. Google Maps Client

- [ ] 4.1 Create `internal/infrastructure/maps/google/` package with `Client` struct
- [ ] 4.2 Implement `SearchPlace(ctx, name, adminArea string) (*Place, error)` using Places Text Search API
- [ ] 4.3 Add `Place` response struct with `PlaceID`, `Name` fields
- [ ] 4.4 Add unit test for `SearchPlace` using `httptest` server
- [ ] 4.5 Wire Google Maps API key into config (`internal/di/`)

## 5. Repository Layer

- [ ] 5.1 Update `insertVenueQuery` in `venue_repo.go` to include `enrichment_status` and `raw_name`; if `Venue.EnrichmentStatus` is zero-value (`""`), the repository SHALL substitute `entity.EnrichmentStatusPending` before binding to avoid inserting an invalid ENUM value
- [ ] 5.2 Update `getVenueQuery` and `getVenueByNameQuery` to SELECT `mbid`, `google_place_id`, `enrichment_status`, `raw_name`; update `GetByName` to also match on `raw_name` so enriched venues (renamed to canonical name) can still be found by the original scraper-provided name
- [ ] 5.3 Update `Create()`, `Get()`, `GetByName()` Scan/Exec calls to include new fields
- [ ] 5.4 Implement `ListPending(ctx)` query: `SELECT … FROM venues WHERE enrichment_status = 'pending'`
- [ ] 5.5 Implement `UpdateEnriched(ctx, venue)` query: copy current `name` to `raw_name` (if `raw_name` is NULL), UPDATE `name` to canonical, set `mbid` or `google_place_id`, set `enrichment_status = 'enriched'`
- [ ] 5.6 Implement `MarkFailed(ctx, id)` query: UPDATE `enrichment_status = 'failed'`
- [ ] 5.7 Implement `MergeVenues(ctx, canonicalID, duplicateID string)` — atomic transaction: 1) DELETE events in the duplicate venue that share `(artist_id, local_event_date, start_at)` (NULL-safe equality via `IS NOT DISTINCT FROM`) with the canonical venue; 2) UPDATE remaining `events.venue_id` to `canonicalID`; 3) UPDATE canonical venue fields using `COALESCE` for `admin_area`, `mbid`, `google_place_id`; 4) DELETE duplicate venue
- [ ] 5.8 Update `venue_repo_test.go` to cover all new fields and methods

## 6. Venue Enrichment Use Case

- [ ] 6.1 Create `internal/usecase/venue_enrichment_uc.go` with `VenueEnrichmentUseCase` interface and `venueEnrichmentUseCase` struct
- [ ] 6.2 Implement `EnrichPendingVenues(ctx)`: iterate `ListPending`, call MB then Maps, merge duplicates or update, mark failed on both miss
- [ ] 6.3 Implement duplicate detection: after resolving external ID, query for existing venue with same MBID/place_id; if found, call `MergeVenues`
- [ ] 6.4 Write unit tests in `venue_enrichment_uc_test.go` covering: MB hit, Maps fallback hit, both miss, ambiguous results (multiple matches → failed), duplicate merge (admin_area / mbid / google_place_id COALESCE)

## 7. Concert Discovery Job Integration

- [ ] 7.1 Add `VenueEnrichmentUseCase` to job DI initializer in `internal/di/job.go`
- [ ] 7.2 Call `EnrichPendingVenues(ctx)` as a post-step after all artists are processed in the job entrypoint
- [ ] 7.3 Ensure per-venue errors are logged and non-fatal (job exits with status 0)

## 8. Concert Service — Venue Creation Update

- [ ] 8.1 Update `concert_uc.go` venue creation to set `EnrichmentStatus = entity.EnrichmentStatusPending` and `RawName = name` explicitly on the `Venue` entity before calling `Create()` — the repository layer's zero-value guard is a safety net, not the primary path
