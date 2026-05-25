## MODIFIED Requirements

### Requirement: Generic Event Management

The system SHALL support a generic `Event` entity that represents a single performance occurring on a specific date at a specific venue. Each `Event` SHALL encapsulate per-occurrence properties: `EventId`, `SeriesId` (parent reference), `Venue`, `LocalEventDate`, `StartTime`, and `OpenTime`. The `EventId` message SHALL be defined in `event.proto` as the canonical event identifier for the platform.

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
- **THEN** it SHALL NOT contain a `Title`, `Url source_url`, or any field representing series-level metadata
- **AND** retrieving the title or source URL for an event SHALL require resolving its parent `Series`

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

## ADDED Requirements

### Requirement: Series as Parent Aggregation

The system SHALL support a `Series` entity that aggregates one or more `Event` rows representing a tour, a multi-day single-venue run, or a festival. Each `Event` MUST belong to exactly one `Series`. A `Series` SHALL own the metadata that is common across all its events.

The `Series` entity SHALL include: `SeriesId`, `Title`, `SeriesType` (one of `TOUR`, `SINGLE`, `FESTIVAL`), and an optional `source_url`. The `SeriesType` enum SHALL be designed as additive — new values MAY be appended without breaking existing consumers.

#### Scenario: Series owns shared metadata

- **WHEN** a tour spans multiple stops on different dates and venues
- **THEN** the tour title and source URL SHALL be stored on the parent `Series` row exactly once
- **AND** each stop SHALL be persisted as a separate `Event` row referencing the same `series_id`

#### Scenario: Every Event belongs to a Series

- **WHEN** an `Event` is created
- **THEN** the `series_id` foreign key SHALL be non-null and reference an existing `Series` row
- **AND** even a one-off single-day concert SHALL have a `Series` row created for it (typically with `type = SINGLE`)

#### Scenario: SeriesType enumerates supported series shapes

- **WHEN** a `Series` is created
- **THEN** its `type` SHALL be one of `TOUR`, `SINGLE`, or `FESTIVAL`
- **AND** the `SERIES_TYPE_UNSPECIFIED` value SHALL never be persisted

#### Scenario: Series natural identity is not enforced at the database layer

- **WHEN** two distinct `Series` rows with similar or identical titles are inserted
- **THEN** the database SHALL accept both writes
- **AND** deduplication SHALL be performed at the application layer using fuzzy matching on title and related fields

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

### Requirement: Event Natural Key Reflects Series Membership

The natural key of `events` SHALL be `(series_id, local_event_date, venue_id)`. The previous key `(artist_id, local_event_date)` SHALL be removed because `artist_id` no longer exists on `events`.

#### Scenario: Same series cannot have two events at the same venue on the same date

- **WHEN** an attempt is made to insert a second `Event` row for the same `series_id`, `local_event_date`, and `venue_id`
- **THEN** the database SHALL reject the insert with a unique-constraint violation

#### Scenario: Different series at the same venue on the same date are allowed

- **WHEN** two distinct `Series` rows have events at the same venue on the same date
- **THEN** both events SHALL be persisted successfully

### Requirement: Concert DTO Embeds Series and Performers

The `Concert` proto message SHALL embed the full `Series` parent and SHALL expose performing artists via `repeated Artist performers`, so that a single RPC response carries all data needed to render the event to a user.

The `Concert` message SHALL NOT contain `Title title` or `Url source_url` fields; those values SHALL be accessed through the embedded `Series`.

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
