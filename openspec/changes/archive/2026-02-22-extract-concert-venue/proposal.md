## Why

To support location-based dashboard filtering (showing users concerts near their home prefecture), the Gemini-extracted concert data must include the venue's administrative area (`admin_area`). Additionally, the raw venue name as listed on the artist's official site needs to be preserved on the Event entity, distinct from the future normalized `Venue.Name` that will come from Google Maps / MusicBrainz.

## What Changes

- Add `admin_area` field to the Gemini JSON schema and prompt, instructing the model to extract the prefecture-level location (or international equivalent) from the venue name or surrounding page context. If uncertain, the field is left empty — wrong values are strictly forbidden.
- Rename `ScrapedConcert.VenueName` → `ListedVenueName` to distinguish the raw scraped name from the normalized `Venue.Name`.
- Add `ScrapedConcert.AdminArea *string` to carry the extracted area through the processing pipeline.
- Add `Venue.AdminArea *string` and persist it in the `venues` table.
- Add `Event.ListedVenueName string` and persist it in the `events` table, preserving the original source text for future normalization workflows.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `concert-search`: Gemini extraction now returns `admin_area` in addition to existing fields. `ScrapedConcert` gains `ListedVenueName` (renamed from `VenueName`) and `AdminArea *string`.
- `concert-service`: Venue creation includes `AdminArea`; Event creation includes `ListedVenueName`. DB schema gains `venues.admin_area` and `events.listed_venue_name` columns.

## Impact

- **Backend Go**: `entity`, `usecase`, `infrastructure/gcp/gemini`, `infrastructure/database/rdb` packages
- **Proto / API**: `venue.proto` — add `admin_area` field; `mapper/concert.go` updated
- **Database**: New migration — `ALTER TABLE venues ADD COLUMN admin_area TEXT`, `ALTER TABLE events ADD COLUMN listed_venue_name TEXT`
- **Tests**: `concert_uc_test.go`, `venue_repo_test.go`, `searcher_test.go` — field rename and new field assertions
