## MODIFIED Requirements

### Requirement: Series as Parent Aggregation

The system SHALL support a `Series` entity that aggregates one or more `Event` rows representing a tour, a multi-day single-venue run, or a festival. Each `Event` SHALL belong to exactly one `Series`. A `Series` SHALL own the metadata that is common across all its events.

The `Series` entity SHALL include: `SeriesId`, `Title`, `SeriesType`, an optional `source_url`, and an optional `merch_url`. Both `source_url` and `merch_url` are of type `Url` and follow identical optionality semantics: a nil wrapper is valid and skips inner-`Url` validation, while a present wrapper SHALL satisfy the `Url` value-object constraints. `merch_url` SHALL point to the official merchandise information page shared across the series; it carries no sale timing, channel, or item data — those remain on the linked page. The `SeriesType` enum SHALL declare:

- `SERIES_TYPE_UNSPECIFIED = 0` — the proto3-mandated zero-value sentinel; rejected at the proto boundary by `(buf.validate.field).enum.not_in = [0]` so it can never be persisted.
- `SERIES_TYPE_TOUR = 1` — a series of events at multiple venues by the same set of performers, typically branded with a tour name.
- `SERIES_TYPE_SINGLE = 2` — a standalone engagement at a single venue, spanning one or more consecutive days.
- `SERIES_TYPE_FESTIVAL = 3` — a multi-performer event such as a music festival.

The proto-prefixed identifiers above are enforced by `buf lint ENUM_VALUE_PREFIX` and match the generated Go / TS constants; the bare `TOUR` / `SINGLE` / `FESTIVAL` aliases used elsewhere in this spec refer to the same values in prose. The `SeriesType` enum SHALL be designed as additive — new non-zero values MAY be appended without breaking existing consumers.

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

#### Scenario: Series natural identity is not enforced at the database layer

- **WHEN** two distinct `Series` rows with similar or identical titles are inserted
- **THEN** the database SHALL accept both writes
- **AND** deduplication SHALL be performed at the application layer using fuzzy matching on title and related fields
