## 1. Simplify resolveVenue — Skip Unresolvable Concerts

- [ ] 1.1 Change `resolveVenue` return signature to `(venueID, *Venue, skip bool, err)` — return `skip=true` when Places API returns NotFound or non-retryable error
- [ ] 1.2 Add structured Warn log on skip with all `ScrapedConcert` fields (title, local_date, start_time, open_time, listed_venue_name, admin_area, source_url)
- [ ] 1.3 Remove `GetByName` fallback from `resolveVenue`
- [ ] 1.4 Remove `createVenuePending()` method
- [ ] 1.5 Remove `venue.created.v1` publish loop from `CreateFromDiscovered`
- [ ] 1.6 Update `CreateFromDiscovered` to skip concerts where `resolveVenue` returns `skip=true`
- [ ] 1.7 Make `placeSearcher` required: panic in `NewConcertCreationUseCase` if nil
- [ ] 1.8 Update unit tests for `concert_creation_uc_test.go`

## 2. Remove Venue Enrichment Pipeline

- [ ] 2.1 Delete `usecase/venue_enrichment_uc.go` and `venue_enrichment_uc_test.go`
- [ ] 2.2 Delete `adapter/event/venue_consumer.go` and `venue_consumer_test.go`
- [ ] 2.3 Remove `VenueEnrichmentUseCase` interface
- [ ] 2.4 Remove `VenueNamedSearcher` type
- [ ] 2.5 Remove `VenueCreatedData` and `SubjectVenueCreated` from `entity/event_data.go`

## 3. Remove Enrichment Repository Methods

- [ ] 3.1 Remove `VenueEnrichmentRepository` interface from `entity/venue.go`
- [ ] 3.2 Remove `ListPending`, `MarkFailed`, `UpdateEnriched`, `MergeVenues` from `rdb/venue_repo.go`
- [ ] 3.3 Remove `GetByName` from `VenueRepository` interface and `rdb/venue_repo.go`
- [ ] 3.4 Update `rdb/venue_repo_test.go` — remove tests for deleted methods
- [ ] 3.5 Remove `AdminAreaResolver` interface and implementation if only used by enrichment

## 4. Clean Up Entity and Schema

- [ ] 4.1 Remove `EnrichmentStatus` constants and field from `entity/venue.go`
- [ ] 4.2 Remove `RawName` field from `entity/venue.go`
- [ ] 4.3 Remove `MBID` field from `entity/venue.go`
- [ ] 4.4 Update `rdb/venue_repo.go` Create method — remove `enrichment_status`, `raw_name`, `mbid` from INSERT
- [ ] 4.5 Update all venue-related test helpers and raw SQL INSERTs to remove dropped columns
- [ ] 4.6 Update `entity/venue_test.go` — remove tests for deleted fields

## 5. Database Migration

- [ ] 5.1 Update `schema.sql` — drop `enrichment_status`, `raw_name`, `mbid` columns, `venue_enrichment_status` enum, `idx_venues_mbid` index
- [ ] 5.2 Create migration: drop columns and enum from `venues` table
- [ ] 5.3 Run `atlas migrate validate --env local`

## 6. DI Wiring

- [ ] 6.1 Remove venue enrichment wiring from `di/consumer.go` (MusicBrainz venue searcher, Google Maps venue searcher, `VenueEnrichmentUseCase`, `VenueConsumer`, router handler)
- [ ] 6.2 Remove `placeSearcher` nil-guard from DI — ensure it's always provided
- [ ] 6.3 Run `mockery` to regenerate mocks

## 7. Verification

- [ ] 7.1 Run `make check` (lint + tests)
- [ ] 7.2 Run `atlas migrate diff --env local` to verify schema.sql matches migrations
