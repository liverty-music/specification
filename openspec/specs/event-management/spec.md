# event-management Specification

## Purpose

The Event Management capability handles the lifecycle of generic events, providing a foundation for specific event types like concerts. It ensures consistent handling of common event data such as titles, dates, times, and venues.
## Requirements
### Requirement: Generic Event Management

The system SHALL support a generic `Event` entity that represents a single performance occurring on a specific date at a specific venue. Each `Event` SHALL encapsulate per-occurrence properties: `EventId`, `SeriesId` (parent reference), `Venue` (embedded message; the DB stores the relationship as a scalar `venue_id` FK and the server hydrates the full `Venue` on read), `local_date` of type `LocalDate` (the DB column is named `local_event_date`), `StartTime`, and `OpenTime`. The `EventId` message SHALL be defined in `event.proto` as the canonical event identifier for the platform.

Series-level metadata (title, source URL, type) SHALL NOT be stored on `Event`; those properties belong to the parent `Series` entity.

#### Scenario: Event Persistence

- **WHEN** a generic event is created
- **THEN** it is persisted in the `events` table with a unique identifier
- **AND** it is associated with exactly one `Series` via a required `series_id` foreign key
- **AND** it can be retrieved independently of specific event types (like `Concert`)

#### Scenario: EventId is the canonical event identifier

- **WHEN** any entity or RPC references an event identifier
- **THEN** it SHALL use `EventId` from `event.proto`
- **AND** `EventId` SHALL NOT be defined in `ticket.proto` or any other file

#### Scenario: Concert uses EventId

- **WHEN** a `Concert` proto message is defined
- **THEN** its `id` field SHALL be of type `EventId` (not `ConcertId`)
- **AND** the `ConcertId` message SHALL NOT exist in the schema

#### Scenario: Event does not carry series-level metadata

- **WHEN** the `Event` proto message is defined
- **THEN** it SHALL NOT contain a `Title title` field (previously occupied field number 3, now reserved) or any other field representing series-level metadata
- **AND** retrieving the title or source URL for an event SHALL require resolving its parent `Series`

> Note: `source_url` was never a field on `Event` — it lived on `Concert` (field 8, now reserved). The series-level relocation applies to both messages: `Concert.title` / `Concert.source_url` were moved to `Series.title` / `Series.source_url`, while `Event` had only `title` to relocate.

### Requirement: Event-Type Extensibility

The system SHALL support extending the base `Event` entity with domain-specific entities (e.g., `Concert`) via a 1:1 relationship. The domain-specific extension table MAY exist as a placeholder for future specialised columns, even when it currently carries no additional fields.

#### Scenario: Concert as Event

- **WHEN** a `Concert` is created
- **THEN** an associated `Event` record is strictly required
- **AND** the `Concert` record shares the same unique identifier (or references it as a foreign key with uniqueness constraint)

#### Scenario: Music-specific extension placeholder is retained

- **WHEN** the `concerts` table contains no music-specific columns beyond `event_id`
- **THEN** the table SHALL still be retained as a placeholder for future music-specific extensions
- **AND** the `Concert` proto message SHALL continue to exist as the user-facing DTO for music events

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

### Requirement: Multiple Performers per Event

The system SHALL support an M:N relationship between `Event` and `Artist` so that a single event can have multiple performing artists (lineups, co-headliners, support acts). The relationship SHALL be modelled as a join entity `event_performers` keyed on `(event_id, artist_id)` with no additional required attributes.

The `Concert` DTO SHALL expose the resolved performers via a repeated field, ensuring downstream consumers do not need to issue an additional query to render an event's lineup.

#### Scenario: Co-headliner persistence

- **WHEN** two artists co-headline an event
- **THEN** two rows SHALL be inserted into `event_performers`, one per artist, each referencing the same `event_id`
- **AND** querying the event's performers SHALL return both artists

#### Scenario: Single-artist event compatibility

- **WHEN** an event has exactly one performer (the common case)
- **THEN** exactly one row SHALL exist in `event_performers` for that event
- **AND** the `Concert.performers` field SHALL contain exactly one `Artist`

#### Scenario: Artist is not duplicated on Event

- **WHEN** the `Event` proto message is defined
- **THEN** it SHALL NOT contain an `ArtistId artist_id` field
- **AND** the performing artists SHALL be retrieved exclusively via the `event_performers` relationship

### Requirement: Concert DTO Embeds Series and Performers

The `Concert` proto message SHALL embed the full `Series` parent and SHALL expose performing artists via `repeated Artist performers`, so that a single RPC response carries all data needed to render the event to a user.

The `Concert` message SHALL NOT contain `Title title` or `Url source_url` fields; those values SHALL be accessed through the embedded `Series`.

The `Concert` message MAY retain `VenueId venue_id` alongside the embedded `Venue venue` field as a backward-compatibility convenience for clients that have not yet migrated to reading `venue.id`. The proto comment on `venue_id` SHALL flag the field as legacy ("prefer the embedded `venue` field"), and a future change SHOULD migrate consumers off it and reserve the field number.

#### Scenario: Concert response carries embedded Series

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `series` field SHALL contain the full `Series` message (not just a `SeriesId`)
- **AND** the client SHALL be able to render the concert without issuing a follow-up call to fetch the `Series`

#### Scenario: Concert response carries all performers

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `performers` repeated field SHALL contain at least one `Artist`
- **AND** all artists associated with the underlying `Event` via `event_performers` SHALL be present in the response

#### Scenario: Concert does not duplicate series-level metadata

- **WHEN** the `Concert` proto message is defined
- **THEN** it SHALL NOT contain a `Title title` field
- **AND** it SHALL NOT contain a `Url source_url` field

### Requirement: Trace context propagation across message broker

The system SHALL propagate W3C Trace Context (traceparent) from the publisher process to the consumer process via message metadata. Consumer-side structured logs SHALL include `trace_id` and `span_id` fields extracted from the propagated trace context.

#### Scenario: Consumer log includes trace fields from publisher trace

- **WHEN** a publisher emits an event while processing a traced request
- **THEN** the consumer handler's structured logs MUST contain `trace_id` and `span_id` fields matching the publisher's trace

#### Scenario: Consumer handler operates within propagated span

- **WHEN** the consumer receives a message with trace context in its metadata
- **THEN** all downstream operations (database queries, nested event publishing) MUST be children of the propagated trace

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

