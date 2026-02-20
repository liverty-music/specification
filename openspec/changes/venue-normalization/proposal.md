## Why

`venues.name` currently stores the raw venue name extracted by Gemini (e.g., "日本武道館", "Nippon Budokan"), which creates duplicate venue records when the same physical location is expressed differently across sources. A normalization pipeline using MusicBrainz (with Google Maps as fallback) is needed to establish canonical venue identities and enable reliable deduplication.

## What Changes

- Add `mbid TEXT` and `google_place_id TEXT` columns to `venues` table (nullable, external identifiers)
- Add `enrichment_status` enum column to `venues` table (`pending` / `enriched` / `failed`)
- Implement a venue enrichment job that resolves raw venue names to canonical identities via MusicBrainz Place API, falling back to Google Maps Places Text Search
- Duplicate venue records sharing the same external ID are detected during enrichment and merged atomically: events are re-pointed to the canonical venue, `admin_area` is preserved via `COALESCE`, and the duplicate is deleted
- Enrichment job runs as a post-step of the existing `concert-discovery` job (piggyback); future migration to event-driven trigger is noted as a follow-up
- Extend MusicBrainz client to support `place` endpoint in addition to existing `artist` endpoint

## Capabilities

### New Capabilities

- `venue-normalization`: Async enrichment pipeline that resolves raw venue names to canonical external IDs (MusicBrainz MBID or Google Maps place_id), merges duplicate venue records, and updates `venues.name` to the canonical form

### Modified Capabilities

- `concert-service`: `Venue` entity gains `MBID`, `GooglePlaceID`, and `EnrichmentStatus` fields; persistence layer updated accordingly

## Impact

- **Backend Go**: `entity/venue.go`, `infrastructure/database/rdb/venue_repo.go`, `infrastructure/music/musicbrainz/client.go` (new `place` endpoint), new `infrastructure/maps/` Google Maps client, new `usecase/venue_enrichment_uc.go`, `cmd/job/` (new enrichment job step)
- **Database**: New migration — `ALTER TYPE` or `CREATE TYPE venue_enrichment_status`, `ALTER TABLE venues ADD COLUMN mbid TEXT, google_place_id TEXT, enrichment_status venue_enrichment_status`
- **Proto / API**: `venue.proto` — add `mbid`, `google_place_id`, `enrichment_status` fields
- **Tests**: `venue_repo_test.go`, new `venue_enrichment_uc_test.go`, MusicBrainz place client tests
