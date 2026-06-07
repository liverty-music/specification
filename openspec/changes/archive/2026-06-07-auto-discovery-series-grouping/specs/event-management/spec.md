## ADDED Requirements

### Requirement: Event Natural Key Reflects Physical Identity

The natural key of the `events` table SHALL be `(venue_id, local_event_date, start_at)`, enforced as a unique constraint that treats NULL `start_at` as equal (`NULLS NOT DISTINCT`) — a database-layer constraint expressed in storage column names; the corresponding proto fields are the embedded `venue.id`, `local_date` (note the proto/DB column rename), and `start_time`. `series_id` SHALL NOT be part of the key: an event's identity is physical (where and when it happens), independent of how it is grouped into a series. The previous key `(series_id, local_event_date, venue_id)` SHALL be removed.

This makes event identity artist- and series-independent, so the same physical show discovered via different artists, series, or source pages resolves to one row; and it makes two performances at the same venue and date with different start times distinct rows.

#### Scenario: Same venue, date, and start time is one event regardless of series

- **WHEN** two discoveries describe the same `(venue_id, local_event_date, start_at)` under different series or source classifications
- **THEN** the database SHALL hold exactly one `Event` row for that key
- **AND** the second discovery SHALL resolve to the existing row (idempotent UPSERT) rather than inserting a duplicate — the unique constraint serves as a race backstop only

#### Scenario: Same venue and date, different start time, are distinct events

- **WHEN** two performances share `(venue_id, local_event_date)` but have different `start_at` values
- **THEN** both `Event` rows SHALL be persisted successfully

#### Scenario: Same venue and date, both start times unpublished, collapse

- **WHEN** two discovered events share `(venue_id, local_event_date)` and both have NULL `start_at`
- **THEN** the `NULLS NOT DISTINCT` constraint SHALL collapse them to a single `Event` row

## MODIFIED Requirements

### Requirement: Series as Parent Aggregation

The system SHALL support a `Series` entity that aggregates one or more `Event` rows representing a tour, a multi-day single-venue run, or a festival. Each `Event` SHALL belong to exactly one `Series`. A `Series` SHALL own the metadata that is common across all its events.

The `Series` entity SHALL include: `SeriesId`, `Title`, `SeriesType`, an optional `source_url`, and an optional `merch_url`. Both `source_url` and `merch_url` are of type `Url` and follow identical optionality semantics: a nil wrapper is valid and skips inner-`Url` validation, while a present wrapper SHALL satisfy the `Url` value-object constraints. `merch_url` SHALL point to the official merchandise information page shared across the series; it carries no sale timing, channel, or item data — those remain on the linked page. The `SeriesType` enum SHALL declare:

- `SERIES_TYPE_UNSPECIFIED = 0` — the proto3-mandated zero-value sentinel; rejected at the proto boundary by `(buf.validate.field).enum.not_in = [0]` so it can never be persisted.
- `SERIES_TYPE_TOUR = 1` — a series of events at multiple venues by the same set of performers, typically branded with a tour name.
- `SERIES_TYPE_SINGLE = 2` — a standalone engagement at a single venue, spanning one or more consecutive days.
- `SERIES_TYPE_FESTIVAL = 3` — a multi-performer event such as a music festival.

The proto-prefixed identifiers above are enforced by `buf lint ENUM_VALUE_PREFIX` and match the generated Go / TS constants; the bare `TOUR` / `SINGLE` / `FESTIVAL` aliases used elsewhere in this spec refer to the same values in prose. The `SeriesType` enum SHALL be designed as additive — new non-zero values MAY be appended without breaking existing consumers.

A `Series` SHALL have no content-derived database key and no database-level uniqueness constraint. Its cross-run identity SHALL be established at the application layer by adopting the `series_id` already carried by its member events (matched on the events' physical natural key), minting a fresh `UUIDv7` `Series` only when no member event yet exists. `series.id` SHALL be a `UUIDv7`.

#### Scenario: Series owns shared metadata

- **WHEN** a tour spans multiple stops on different dates and venues
- **THEN** the tour title and source URL SHALL be stored on the parent `Series` row exactly once
- **AND** each stop SHALL be persisted as a separate `Event` row referencing the same `series_id`

#### Scenario: Series owns the merch URL

- **WHEN** a series has an official merchandise information page
- **THEN** the `merch_url` SHALL be stored on the parent `Series` row exactly once
- **AND** it SHALL be carried through to clients via the embedded `Series` on every `Concert` response

#### Scenario: Merch URL is optional

- **WHEN** a series has no known official merchandise page
- **THEN** the `merch_url` SHALL be absent (nil wrapper)
- **AND** persistence and serialization SHALL succeed without error

#### Scenario: Every Event belongs to a Series

- **WHEN** an `Event` is created
- **THEN** the `series_id` foreign key SHALL be non-null and reference an existing `Series` row
- **AND** even a one-off single-day concert SHALL have a `Series` row created for it (typically with `type = SINGLE`)

#### Scenario: SeriesType enumerates supported series shapes

- **WHEN** a `Series` is created
- **THEN** its `type` SHALL be one of `SERIES_TYPE_TOUR`, `SERIES_TYPE_SINGLE`, or `SERIES_TYPE_FESTIVAL`
- **AND** the `SERIES_TYPE_UNSPECIFIED` value SHALL never be persisted

#### Scenario: Series identity is derived from member events, not a database key

- **WHEN** a tour group is persisted and at least one of its events already exists
- **THEN** the group SHALL adopt the existing events' `series_id` rather than minting a new one
- **AND** when no member event exists, a new `UUIDv7` `Series` SHALL be created
- **AND** the database SHALL NOT enforce any uniqueness on `Series` title or other content

## REMOVED Requirements

### Requirement: Event Natural Key Reflects Series Membership

**Reason**: Replaced by "Event Natural Key Reflects Physical Identity". The events natural key no longer embeds `series_id` — event identity is physical `(venue_id, local_event_date, start_at)`, independent of series grouping.

**Migration**: Backend migration `20260605120000_rework_event_natural_key_and_series_id` swaps the constraint (deduplicating colliding rows first). See the `auto-discovery-series-grouping` change.
