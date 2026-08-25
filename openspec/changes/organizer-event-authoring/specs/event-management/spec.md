## MODIFIED Requirements

### Requirement: Series as Parent Aggregation

The system SHALL support a `Series` entity that aggregates one or more `Event` rows representing a tour, a multi-day single-venue run, or a festival. Each `Event` SHALL belong to exactly one `Series`. A `Series` SHALL own the metadata that is common across all its events.

The `Series` entity SHALL include: `SeriesId`, `Title`, `SeriesType`, an optional `source_url`, and — for organizer-authored series — an optional `description`, an optional `cover_image`, a `visibility`, a `publish_state`, and an `organizer_id`. `source_url` and `cover_image` are of type `Url` and follow these optionality semantics: a nil wrapper is valid and skips inner-`Url` validation, while a present wrapper SHALL satisfy the `Url` value-object constraints. `description` is a `Description` value object with protovalidate length bounds. `organizer_id` is non-null exactly when the series is organizer-authored (first-party); a null `organizer_id` denotes a discovery-created series. The `SeriesType` enum SHALL declare:

- `SERIES_TYPE_UNSPECIFIED = 0` — the proto3-mandated zero-value sentinel; rejected at the proto boundary by `(buf.validate.field).enum.not_in = [0]` so it can never be persisted.
- `SERIES_TYPE_TOUR = 1` — a series of events at multiple venues by the same set of performers, typically branded with a tour name.
- `SERIES_TYPE_SINGLE = 2` — a standalone engagement at a single venue, spanning one or more consecutive days.
- `SERIES_TYPE_FESTIVAL = 3` — a multi-performer event such as a music festival.

The proto-prefixed identifiers above are enforced by `buf lint ENUM_VALUE_PREFIX` and match the generated Go / TS constants; the bare `TOUR` / `SINGLE` / `FESTIVAL` aliases used elsewhere in this spec refer to the same values in prose. The `SeriesType` enum SHALL be designed as additive — new non-zero values MAY be appended without breaking existing consumers.

A `Series` SHALL carry a lifecycle for organizer-authored series: `visibility` is one of `PUBLIC` / `UNLISTED` (with `PASSWORD` reserved for a later change), and `publish_state` is one of `DRAFT` / `PUBLISHED` / `CANCELLED` (with `SCHEDULED` reserved). Only a `PUBLISHED` + `PUBLIC` series surfaces in discovery and follower lists; `DRAFT`, `UNLISTED`, and `CANCELLED` series SHALL be excluded from fan-facing surfaces. Discovery-created series (null `organizer_id`) behave as `PUBLISHED` + `PUBLIC` by default.

A `Series` SHALL have no content-derived database key and no database-level uniqueness constraint. Its cross-run identity SHALL be established at the application layer by adopting the `series_id` already carried by its member events (matched on the events' physical natural key), minting a fresh `UUIDv7` `Series` only when no member event yet exists. `series.id` SHALL be a `UUIDv7`.

#### Scenario: Series owns shared metadata

- **WHEN** a tour spans multiple stops on different dates and venues
- **THEN** the tour title and source URL SHALL be stored on the parent `Series` row exactly once
- **AND** each stop SHALL be persisted as a separate `Event` row referencing the same `series_id`

#### Scenario: Every Event belongs to a Series

- **WHEN** an `Event` is created
- **THEN** the `series_id` foreign key SHALL be non-null and reference an existing `Series` row

#### Scenario: SeriesType enumerates supported series shapes

- **WHEN** a `Series` is created
- **THEN** its `type` SHALL be one of `SERIES_TYPE_TOUR`, `SERIES_TYPE_SINGLE`, or `SERIES_TYPE_FESTIVAL`
- **AND** the `SERIES_TYPE_UNSPECIFIED` value SHALL never be persisted

#### Scenario: Series identity is derived from member events, not a database key

- **WHEN** a tour group is persisted and at least one of its events already exists
- **THEN** the group SHALL adopt the existing events' `series_id` rather than minting a new one
- **AND** when no member event exists, a new `UUIDv7` `Series` SHALL be created
- **AND** the database SHALL NOT enforce any uniqueness on `Series` title or other content

#### Scenario: Organizer-authored series carry authoring metadata and lifecycle

- **WHEN** an organizer authors a first-party series
- **THEN** the `Series` SHALL carry a non-null `organizer_id`, its `visibility`, its `publish_state`, and any `description` / `cover_image`
- **AND** the series SHALL surface to fans only while `PUBLISHED` + `PUBLIC`
