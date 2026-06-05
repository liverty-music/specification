## ADDED Requirements

### Requirement: Tour Events Group Into a Single Series

The system SHALL persist all events that Gemini grouped under one `<tour>` block as a single `Series` with `SeriesType = SERIES_TYPE_TOUR`, shared by every event in the group. This replaces the prior 1-`Series`-per-`Event` SINGLE fallback for tours.

#### Scenario: Multi-stop tour creates one TOUR series

- **WHEN** a discovered tour group contains three events at different venues/dates
- **THEN** exactly one `Series` row SHALL be created with `type = SERIES_TYPE_TOUR`
- **AND** all three `Event` rows SHALL reference that single `series_id`
- **AND** the tour title and source URL SHALL be stored once on that `Series`

#### Scenario: Single-date tour block still yields a TOUR series

- **WHEN** a `<tour>` group contains only one event within the search window
- **THEN** the created `Series` SHALL have `type = SERIES_TYPE_TOUR`
- **AND** the SeriesType SHALL NOT be downgraded based on the event count

### Requirement: Series Identity Is Adopted From Member Events

The system SHALL establish a `Series`'s cross-run identity from the events that already belong to it, not from any content-derived key. When persisting a tour group, the system SHALL reuse the `series_id` carried by the group's already-persisted events (matched by the events' physical natural key); only when no member event yet exists SHALL it mint a fresh `UUIDv7` `Series`. A `Series` SHALL have no content-derived database key and no database-level uniqueness constraint, and `series.id` SHALL be a `UUIDv7`.

#### Scenario: Re-discovery adopts the existing series

- **WHEN** a tour is discovered again on a later run and at least one of its events already exists
- **THEN** the tour group SHALL reuse the existing event's `series_id`
- **AND** no duplicate `Series` row SHALL be created

#### Scenario: A genuinely new tour mints a fresh series

- **WHEN** a tour group's events do not yet exist in the database
- **THEN** a new `Series` row SHALL be created with a `UUIDv7` identifier
- **AND** every event in the group SHALL reference that new `series_id`

#### Scenario: Divergent-title co-headline tour converges to one series

- **WHEN** the same real tour is discovered via two artists with divergent titles and no shared `source_url`
- **THEN** the second discovery's events SHALL match the first's by physical natural key
- **AND** SHALL adopt the existing `series_id`
- **AND** exactly one TOUR `Series` SHALL exist for the tour, with both artists linked via `event_performers`

### Requirement: Events Deduplicate On Physical Natural Key

The events natural key SHALL be `(venue_id, local_event_date, start_at)`, enforced as a unique constraint that treats NULL `start_at` values as equal (`NULLS NOT DISTINCT`). The key SHALL NOT include `series_id`. Two performances at the same venue and date with different start times SHALL be distinct events; two with the same venue, date, and start time SHALL be the same event regardless of which series or artist discovered them.

#### Scenario: Matinee and evening shows are distinct events

- **WHEN** two performances occur at the same venue on the same date with different `start_at` values
- **THEN** two distinct `Event` rows SHALL be persisted

#### Scenario: Same physical show discovered via two artists is one event

- **WHEN** the same `(venue_id, local_event_date, start_at)` show is discovered separately via two followed artists
- **THEN** it SHALL resolve to a single `Event` row
- **AND** both artists SHALL be linked via `event_performers`

#### Scenario: Two unpublished-time shows at one venue/date collapse

- **WHEN** two discovered events share `(venue_id, local_event_date)` and both lack a published `start_at`
- **THEN** they SHALL collapse to a single `Event` row

### Requirement: Event Identity Is Resolved In The Application

The system SHALL resolve each scraped event against existing rows before writing, so that a later-announced `start_at` updates the row first seen with a NULL start rather than inserting a duplicate, while a genuinely new start time at the same venue/date is inserted as a new event.

#### Scenario: Later-announced start time fills the existing row

- **WHEN** an event was first persisted with a NULL `start_at`
- **AND** a subsequent discovery provides a concrete `start_at` for the same `(venue_id, local_event_date)`
- **THEN** the existing row's `start_at` SHALL be filled in
- **AND** no duplicate `Event` row SHALL be created

#### Scenario: A new start time at a known venue/date is a new event

- **WHEN** an existing row at `(venue_id, local_event_date)` already has a concrete `start_at`
- **AND** a discovery provides a different concrete `start_at` for the same venue and date
- **THEN** a new `Event` row SHALL be inserted (a distinct session)

### Requirement: SeriesType Assigned From Source Classification

The system SHALL assign `SeriesType` from the Gemini block the event originated in — TOUR for `<tour>`, SINGLE for `<standalone>` — and SHALL NOT infer it from the number of events.

#### Scenario: Multi-day standalone stays SINGLE

- **WHEN** a `<standalone>` block describes a multi-day single-venue run
- **THEN** its `Series` SHALL have `type = SERIES_TYPE_SINGLE`

#### Scenario: Standalone is not grouped into a tour

- **WHEN** a `<standalone>` event shares a title with a tour
- **THEN** it SHALL NOT be folded into the tour's `Series`
- **AND** it SHALL receive its own SINGLE series

### Requirement: Multi-Hall Venues Are Disambiguated By venue_id

The system SHALL rely on `venue_id` resolution to distinguish concurrent performances in different halls of the same building. The events natural key SHALL NOT include raw venue text. When a source names the hall, distinct halls SHALL resolve to distinct `venue_id`s; when a source omits the hall, the reference MAY resolve to the building-level venue.

#### Scenario: Different halls on the same date are distinct events

- **WHEN** two performances on the same date are listed with distinct hall names of the same building (e.g. ホールA and ホールC)
- **THEN** they SHALL resolve to distinct `venue_id`s
- **AND** SHALL be persisted as two distinct `Event` rows

### Requirement: Residual Grouping Ambiguities Are Logged, Not Fatal

The system SHALL treat residual grouping ambiguities as non-fatal and SHALL log them rather than failing discovery.

#### Scenario: Late additional dates after full rotation may split

- **WHEN** a tour's previously-seen dates have all passed and been range-filtered before newly-announced dates are discovered
- **THEN** the system MAY create a second TOUR `Series` for the new dates
- **AND** discovery SHALL complete successfully without error

#### Scenario: Hall name omitted by one source may split

- **WHEN** the same physical show is discovered once with a hall name and once without
- **THEN** it MAY resolve to two `venue_id`s and two `Event` rows
- **AND** discovery SHALL complete successfully, logging the anomaly
