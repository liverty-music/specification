## Why

The current `Event` entity flattens every concert into a single row, duplicating tour-level metadata (title, source URL) across each day of a tour or festival. This blocks tour-scoped notifications, tour-overview UI, and per-tour ticket-purchase URLs, and forces Gemini-based auto-discovery to redundantly extract the same series-level fields per stop. The single-`artist_id` shape on `events` and `concerts` also cannot represent festival lineups or co-headlining (対バン).

Introducing a `Series` parent entity and an M:N artist relation aligns the data model with the music-industry convention (Schema.org `Event`+`subEvent`, Songkick `Event`+`Performance`, Eventbrite `Series`+`Occurrence`) and unblocks the above use cases without forcing downstream consumers to change their primary API surface (the existing `Concert` proto remains the user-facing DTO).

## What Changes

- **BREAKING (DB)**: Introduce a `series` table that owns the tour/festival/single-run metadata (`title`, `type`, `source_url`).
- **BREAKING (DB)**: Slim the `events` table: drop `artist_id`, `title`, `source_url`; add required `series_id` FK; replace the natural key `(artist_id, local_event_date)` with `(series_id, local_event_date, venue_id)`.
- **BREAKING (DB)**: Introduce `event_performers` (M:N `event_id` × `artist_id`) so any event can have multiple performing artists (festivals, co-headliners, support acts).
- **BREAKING (DB)**: Drop `concerts.artist_id`; the column is now redundant with `event_performers`. The `concerts` table itself stays as a placeholder for future music-specific extensions.
- **BREAKING (DB)**: Existing rows in `events` (and all FK-cascaded rows in `tickets`, `ticket_journeys`, `ticket_emails`, `merkle_tree`, `nullifiers`) are dropped during migration. Production has not been released yet, so no data rescue is required.
- **BREAKING (proto)**: Add a new `series.proto` (`Series`, `SeriesId`, `SeriesType` enum with values `TOUR`, `SINGLE`, `FESTIVAL`).
- **BREAKING (proto)**: Rewrite `event.proto`'s `Event` message to mirror the slimmed schema (drop `title`; add required `series_id`).
- **BREAKING (proto)**: Modify `concert.proto`'s `Concert` message: drop `title` and `source_url` (now in `Series`); replace `artist_id` with `repeated Artist performers`; embed the full `Series` message so a single RPC response carries everything the UI needs.

## Capabilities

### New Capabilities

(None — `Series` is a new entity inside the existing event-management capability rather than a standalone capability.)

### Modified Capabilities

- `event-management`: parent/child hierarchy (Series owns Event), M:N performers, replacement natural key, and the `Concert` DTO's new shape.

## Impact

- **Affected code (specification repo)**: `proto/liverty_music/entity/v1/event.proto`, `proto/liverty_music/entity/v1/concert.proto`, new `proto/liverty_music/entity/v1/series.proto`.
- **Affected code (backend repo, downstream)**: every repository, use case, and handler that currently reads `events.title`, `events.source_url`, `events.artist_id`, or `concerts.artist_id`; `ConcertService` handler must JOIN `series` and `event_performers` to populate the `Concert` DTO; `SearchNewConcerts` (auto-discovery) must persist a `Series` row per discovered event. Detailed handler/usecase changes are out of scope for this change and tracked separately.
- **Affected code (frontend repo, downstream)**: regenerated `Concert` type carries `Series series` and `repeated Artist performers` instead of `title`/`source_url`/`artist_id`. Display code must be updated.
- **Migration**: `TRUNCATE events CASCADE` plus DDL — single Atlas migration file.
- **Breaking change semantics**: this is a `BREAKING` proto change. Requires `buf skip breaking` label on the specification PR. Downstream (backend, frontend) PRs depend on the BSR release for the new generated types.
