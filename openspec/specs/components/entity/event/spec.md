# Event

## Purpose

Defines the Event entity representing a single performance occurrence at a venue on a given date and time, identified by venue, date, and start time, and supporting multiple performing artists.

## Requirements

### Requirement: Listed Venue Name Preservation

The system SHALL preserve the raw venue name as found on the artist's official site on the Event record, separate from the normalized `Venue.Name`. This ensures the original source text is available for future normalization workflows (e.g., matching against Google Maps or MusicBrainz).

#### Scenario: Listed venue name stored on event creation

- **WHEN** a new concert event is persisted
- **THEN** the `listed_venue_name` field on the event SHALL contain the exact venue name string returned by the Gemini extraction

#### Scenario: Listed venue name is non-empty for discovered concerts

- **WHEN** Gemini returns a non-empty venue string for a concert
- **THEN** `listed_venue_name` on the persisted event SHALL be that string

### Requirement: Event Natural Key Constraint

The `events` table SHALL have a composite UNIQUE constraint on the natural key `(venue_id, local_event_date, start_at)` to prevent duplicate event rows at the database level. This constraint serves as the final safety net when application-level dedup fails.

#### Scenario: Duplicate event insert is rejected

- **WHEN** a concert is inserted with the same `(venue_id, local_event_date, start_at)` as an existing event
- **THEN** the database SHALL reject the insert via the UNIQUE constraint
- **AND** the application SHALL handle this gracefully via UPSERT (not error)

#### Scenario: NULL-safe equality for start_at in constraint

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** both have `start_at = NULL`
- **THEN** the UNIQUE constraint SHALL treat them as duplicates
- **AND** the constraint SHALL use a `UNIQUE NULLS NOT DISTINCT` clause or a partial unique index to handle NULL equality

#### Scenario: Same venue and date with different start_at

- **WHEN** two events have the same `venue_id` and `local_event_date`
- **AND** different non-NULL `start_at` values
- **THEN** the UNIQUE constraint SHALL allow both rows (matinee/evening shows)

### Requirement: Event represents a single performance occurrence

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

### Requirement: Event supports multiple performing artists

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

### Requirement: Event identity is keyed on venue, date, and start time

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

### Requirement: Invalid calendar components SHALL NOT silently roll over

When the library is asked to interpret a `CalendarDate` (or produce one from arithmetic) whose components do not denote a real calendar day (for example a zero or negative month, or a month/day outside its valid domain), it SHALL surface the invalidity as a rejection (a "no value" / null-equivalent result at the boundary) rather than silently normalizing it to a different real date. This closes the native-`Date` footgun where `new Date(2026, -1, 15)` rolls to 2025-12-15.

#### Scenario: Zero-month input does not roll into the previous year

- **WHEN** the library is asked to interpret a `CalendarDate` with `month = 0` (or any out-of-domain component)
- **THEN** it SHALL reject the value at the boundary (a "no value" / null-equivalent result)
- **AND** it SHALL NOT return a `CalendarDate` denoting a rolled-over date in an adjacent month or year
