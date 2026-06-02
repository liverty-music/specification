## ADDED Requirements

### Requirement: Tour Events Are Grouped Into a Single Series

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

### Requirement: Deterministic Tour Series Identity

The system SHALL derive a tour's `seriesID` deterministically so that re-discovering the same tour converges to the same `Series` row rather than minting a new one.

#### Scenario: Stable across re-discovery

- **WHEN** the same tour is discovered again on a later run
- **THEN** the derived `seriesID` SHALL be identical to the previous run's
- **AND** no duplicate `Series` row SHALL be created for that tour

#### Scenario: Tour identity derived from a tour-specific source URL with title fallback

- **WHEN** a tour group has a non-empty `source_url` that is a tour-specific page
- **THEN** the `seriesID` SHALL be derived deterministically from that `source_url`
- **AND** when `source_url` is absent, it SHALL be derived from the artist-scoped normalized tour title

#### Scenario: Generic (non-tour-specific) source URL is treated as absent

- **WHEN** a tour group's `source_url` resolves to a generic index page (e.g. an artist `/live` or `/news` root, or a shared label / agency / promoter page) rather than a tour-specific page
- **THEN** the system SHALL treat the `source_url` as absent for identity purposes
- **AND** SHALL fall back to the artist-scoped normalized tour title, so that unrelated tours sharing a generic URL are not merged into a single `Series`

### Requirement: Standalone Concerts Retain Per-Venue-Date Series

The system SHALL persist standalone concerts (events from a `<standalone>` block) using the existing per-`(venue, date)` deterministic `seriesID` with `SeriesType = SERIES_TYPE_SINGLE`, preserving the artist-independent cross-artist dedup that co-headliner discovery relies on.

#### Scenario: Co-headliner standalone dedups across artists

- **WHEN** the same standalone co-headliner event is discovered separately via two followed artists
- **THEN** both discoveries SHALL derive the same per-`(venue, date)` `seriesID`
- **AND** the event SHALL dedup onto a single `Event` row
- **AND** both artists SHALL be linked via `event_performers`

#### Scenario: Standalone is not grouped into a tour

- **WHEN** a `<standalone>` event shares a title with a tour
- **THEN** it SHALL NOT be folded into the tour's `Series`
- **AND** it SHALL receive a SINGLE series keyed by `(venue, date)`

### Requirement: SeriesType Assigned From Source Classification

The system SHALL assign `SeriesType` from the Gemini block the event originated in — TOUR for `<tour>`, SINGLE for `<standalone>` — and SHALL NOT infer it from the number of events.

#### Scenario: Multi-day standalone stays SINGLE

- **WHEN** a `<standalone>` block describes a multi-day single-venue run
- **THEN** its `Series` SHALL have `type = SERIES_TYPE_SINGLE`

### Requirement: Grouping Limitations Are Logged, Not Fatal

The system SHALL treat residual grouping ambiguities as non-fatal and SHALL log them rather than failing discovery.

#### Scenario: Divergent-title co-headline tour yields duplicate series

- **WHEN** the same real tour is discovered via two artists with divergent titles and no shared `source_url`
- **THEN** the system MAY create two TOUR `Series` rows
- **AND** discovery SHALL complete successfully without error
