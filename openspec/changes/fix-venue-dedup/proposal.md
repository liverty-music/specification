## Why

Venue records are duplicated when different scraping sources use slightly different text for the same physical venue (e.g., "太宰府天満宮 仮殿" vs "太宰府天満宮", "SGCホール有明" vs "SGC HALL ARIAKE"). Because `resolveVenue` uses exact string matching (`GetByName`), each variant creates a separate venue record. This cascades into duplicate events because the DB natural key `(venue_id, local_event_date, start_at)` cannot detect duplicates across different venue IDs. The async enrichment pipeline is designed to merge these later, but it does not always succeed (enrichment failures, timing gaps).

## What Changes

- **Move venue resolution to Google Places API at creation time**: Instead of creating venues from raw text and enriching later, `resolveVenue` will call the Google Places API first to obtain a canonical `place_id` and name, then look up by `google_place_id` for a reliable existence check.
- **Remove venue from the concert dedup key**: Change the application-level dedup key from `(date|venue|start_at)` to `(date|start_at)` and the DB natural key from `(venue_id, local_event_date, start_at)` to `(artist_id, local_event_date, start_at)`, since a single artist cannot perform at two venues simultaneously.
- **Clean up existing duplicate data**: Delete all existing concert/event/venue records and let the discovery pipeline re-populate cleanly.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `venue-normalization`: Venue resolution moves from async post-enrichment to synchronous at creation time using Google Places API. The async enrichment pipeline becomes a fallback for venues not found by Google Places.
- `concert-search`: The dedup natural key changes from `(date|venue|start_at)` to `(date|start_at)` at the application layer, removing venue from the comparison.
- `concert-service`: The DB unique constraint on events changes from `(venue_id, local_event_date, start_at)` to `(artist_id, local_event_date, start_at)`, and a data cleanup migration removes all existing records for a fresh start.

## Impact

- **backend**: `concert_creation_uc.go` (resolveVenue rewrite), `concert_uc.go` (dedup key change), `venue_repo.go` (new `GetByPlaceID`), `concert_repo.go` (upsert query change), DB migration (constraint change + data cleanup)
- **Google Places API cost**: ~$0.032/request for Text Search; expected volume is low (5-10 unique venues per scrape batch)
- **Data**: All existing events, concerts, and orphaned venues will be deleted. The next discovery cron run will re-populate with clean data.
