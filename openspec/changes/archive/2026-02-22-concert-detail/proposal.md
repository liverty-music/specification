## Why

Users discover concerts on the dashboard (live-highway) but tapping a concert item has no destination — there is no detail view. Additionally, venue information is never surfaced to the frontend (hardcoded as "Venue TBD"), making the dashboard's three-lane layout (My City / My Region / Others) non-functional.

## What Changes

- Add `Venue` embed and `listed_venue_name` to the `Concert` proto message so the frontend can display venue names and build Google Maps links
- **BREAKING**: Rename and VO-ify raw-typed fields in `Concert` and `Event` proto messages to align with the Go entity layer:
  - `date` → `local_date` (`LocalDate` VO)
  - `start_time` / `open_time` → `StartTime` / `OpenTime` VO (Timestamp)
  - `title` → `Title` VO (replaces `ConcertTitle`)
  - `source_url` → `SourceUrl` VO
  - `listed_venue_name` → `ListedVenueName` VO (new)
  - `venue_id` in `Event` → `venue` (`Venue` embed)
  - Remove `create_time` / `update_time` from `Event`
- Rename `LocalEventDate` → `LocalDate` in Go `entity.Event`
- Extend `ConcertRepository.ListByArtist` to JOIN venues and populate `Venue` on each concert
- Add Concert Detail UI: hybrid bottom-sheet + URL sync (`/concerts/:id`) on the frontend
- Enable dashboard lane assignment using `venue.admin_area` vs user's stored region

## Capabilities

### New Capabilities

- `concert-detail`: Full concert detail view (hybrid sheet + URL) with venue name, Google Maps link, open/start times, and ticket source link

### Modified Capabilities

- `live-events`: Concert and Event entity definitions updated — VO-ify raw fields, embed Venue, rename `LocalEventDate` → `LocalDate`, remove `Event.create_time`/`update_time`
- `concert-service`: `List` response now includes resolved `Venue` and `listed_venue_name` on each `Concert`

## Impact

- **Proto**: `concert.proto` (field renames + new fields), `event.proto` (field renames + Venue embed + field removals) — BSR breaking change
- **Backend**: `concert_repo.go` (SQL JOIN venues), `mapper/concert.go` (new fields), `entity/event.go` (rename `LocalEventDate`)
- **Frontend**: `dashboard-service.ts` (map venue data), `live-event.ts` (add `adminArea`), new concert-detail route + sheet URL sync, dashboard lane assignment logic
