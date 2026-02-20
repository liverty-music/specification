## 1. Database Migration

- [ ] 1.1 Create `venue_enrichment_status` ENUM type (`pending`, `enriched`, `failed`) in a new migration file
- [ ] 1.2 Add `mbid TEXT`, `google_place_id TEXT`, `enrichment_status venue_enrichment_status NOT NULL DEFAULT 'pending'` columns to `venues` table
- [ ] 1.3 Update `schema.sql` to reflect the new columns and enum type

## 2. Entity Layer

- [ ] 2.1 Add `MBID string`, `GooglePlaceID string`, `EnrichmentStatus string` fields to `Venue` in `internal/entity/venue.go`
- [ ] 2.2 Add `VenueEnrichmentStatus` typed constants (`Pending`, `Enriched`, `Failed`) in `internal/entity/venue.go`
- [ ] 2.3 Create `VenueEnrichmentRepository` interface in `internal/entity/venue.go` with `ListPending(ctx) ([]*Venue, error)` and `UpdateEnriched(ctx, venue) error` and `MarkFailed(ctx, id) error`

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

- [ ] 5.1 Update `insertVenueQuery` in `venue_repo.go` to include `enrichment_status` (defaults to `pending`)
- [ ] 5.2 Update `getVenueQuery` and `getVenueByNameQuery` to SELECT `mbid`, `google_place_id`, `enrichment_status`
- [ ] 5.3 Update `Create()`, `Get()`, `GetByName()` Scan/Exec calls to include new fields
- [ ] 5.4 Implement `ListPending(ctx)` query: `SELECT … FROM venues WHERE enrichment_status = 'pending'`
- [ ] 5.5 Implement `UpdateEnriched(ctx, venue)` query: UPDATE `name`, `mbid` or `google_place_id`, set `enrichment_status = 'enriched'`
- [ ] 5.6 Implement `MarkFailed(ctx, id)` query: UPDATE `enrichment_status = 'failed'`
- [ ] 5.7 Implement `MergeVenues(ctx, canonicalID, duplicateID, adminArea)` — atomic transaction: UPDATE events, UPDATE canonical venue, DELETE duplicate
- [ ] 5.8 Update `venue_repo_test.go` to cover all new fields and methods

## 6. Venue Enrichment Use Case

- [ ] 6.1 Create `internal/usecase/venue_enrichment_uc.go` with `VenueEnrichmentUseCase` interface and `venueEnrichmentUseCase` struct
- [ ] 6.2 Implement `EnrichPendingVenues(ctx)`: iterate `ListPending`, call MB then Maps, merge duplicates or update, mark failed on both miss
- [ ] 6.3 Implement duplicate detection: after resolving external ID, query for existing venue with same MBID/place_id; if found, call `MergeVenues`
- [ ] 6.4 Write unit tests in `venue_enrichment_uc_test.go` covering: MB hit, Maps fallback hit, both miss, duplicate merge, admin_area COALESCE

## 7. Concert Discovery Job Integration

- [ ] 7.1 Add `VenueEnrichmentUseCase` to job DI initializer in `internal/di/job.go`
- [ ] 7.2 Call `EnrichPendingVenues(ctx)` as a post-step after all artists are processed in the job entrypoint
- [ ] 7.3 Ensure per-venue errors are logged and non-fatal (job exits with status 0)

## 8. Concert Service — Venue Creation Update

- [ ] 8.1 Update `concert_uc.go` venue creation to confirm `enrichment_status` is not explicitly set (relies on DB default `'pending'`)
