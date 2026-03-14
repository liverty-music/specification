## Why

The async venue enrichment pipeline (MusicBrainz + Google Maps fallback) is redundant now that `fix-venue-dedup` resolves venues synchronously via Google Places API at concert creation time. When Places API returns NotFound, the enrichment pipeline retries the same search with the same query and almost always fails again, leaving behind unusable venue records (no coordinates, no canonical name, `enrichment_status = 'failed'`). These records provide no value to users and add complexity to the codebase.

By skipping concerts whose venues can't be resolved via Places API and logging the full scraped data for manual review, we eliminate the enrichment pipeline entirely and simplify the venue data model.

## What Changes

- **BREAKING**: `resolveVenue` no longer falls back to name-based lookup or creates pending venues. If Google Places API returns NotFound, the concert is skipped with a structured error log containing all `ScrapedConcert` fields for manual data recovery.
- **BREAKING**: `placeSearcher` becomes a required dependency (no more nil-guard for local dev). Local development must configure a Places API key or use a stub.
- Remove the entire venue enrichment pipeline: `VenueEnrichmentUseCase`, `VenueConsumer`, `venue.created.v1` event, `VenueEnrichmentRepository` interface, and all related repository methods (`ListPending`, `MarkFailed`, `UpdateEnriched`, `MergeVenues`).
- Remove `VenueNamedSearcher`, `AdminAreaResolver` dependency from consumer DI.
- Remove `venue_enrichment_status` enum, `enrichment_status` column, `raw_name` column, and `mbid` column (+ unique index) from the `venues` table.
- Remove `GetByName` from `VenueRepository` interface (no longer used after fallback removal).
- Remove `VenueCreatedData` and `SubjectVenueCreated` from event definitions.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `venue-normalization`: The entire async enrichment pipeline, enrichment status tracking, duplicate merge, and raw_name-based dedup are removed. Venue resolution becomes synchronous-only via Google Places API at concert creation time. Unresolvable venues cause concert records to be skipped rather than created with incomplete data.

## Impact

- **Backend**: `usecase/venue_enrichment_uc.go`, `adapter/event/venue_consumer.go`, related tests, DI wiring, repository methods, and entity fields are deleted. `concert_creation_uc.go` is simplified. Schema migration drops columns/enum.
- **Database**: Migration to drop `enrichment_status`, `raw_name`, `mbid` columns and `venue_enrichment_status` enum. Existing data already cleaned by `fix-venue-dedup` migration.
- **Infrastructure**: MusicBrainz client remains (used by artist name resolution) but is no longer wired into venue enrichment. Google Maps venue searcher in consumer DI is removed (Places API is used in concert creation instead).
- **Observability**: New structured error log for skipped concerts replaces enrichment failure logs.
