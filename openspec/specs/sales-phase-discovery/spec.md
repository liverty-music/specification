# sales-phase-discovery Specification

## Purpose
TBD - created by archiving change add-sales-phase-timeline. Update Purpose after archive.
## Requirements
### Requirement: Dedicated Sales-Phase Searcher

The system SHALL provide a sales-phase searcher, separate from the concert searcher, that discovers a followed artist's ticket-sales phases as series-level records. The searcher SHALL operate **per artist** (not per series): it takes an artist, the artist's seed source URL(s), and the artist's known upcoming series as input, and returns the discovered sale phases mapped back to the correct `series_id`. It SHALL NOT resolve which individual events a phase covers.

The searcher SHALL ground its extraction on a **seeded source URL** (the artist's official site) supplied through the URL-context tool, rather than relying on the model's own memory. It SHALL NOT depend on the Gemini search time-range filter, and SHALL NOT restrict by announcement date — the official site is a live full-state source and re-discovered phases converge idempotently on `(series_id, apply_start_time)`, so only the application-window filter (exclude sales whose application deadline is before today) applies.

#### Scenario: Search sales phases per artist

- **WHEN** the searcher is invoked for an artist with that artist's known upcoming series
- **THEN** it SHALL issue a single grounded Gemini call for the artist (not one call per series)
- **AND** it SHALL ground the call on the artist's seeded source URL via the URL-context tool
- **AND** it SHALL return the discovered sale phases as series-level records, each attributed to one of the supplied `series_id`s

#### Scenario: Map discovered phases to the correct series

- **WHEN** the searcher extracts a sale phase from the grounded source
- **THEN** it SHALL attribute the phase to the matching input `series_id` using the supplied series titles and known event dates
- **AND** a phase that cannot be confidently attributed to a known series SHALL be dropped rather than guessed onto a wrong series

#### Scenario: No covered-event resolution

- **WHEN** the searcher extracts a sale phase
- **THEN** it SHALL NOT extract per-phase covered dates nor resolve them to the series' `event_id`s
- **AND** each extracted phase SHALL carry only its series-level attributes (`apply_start_time` and the descriptive fields)

#### Scenario: One call per artist

- **WHEN** discovery processes multiple artists
- **THEN** the searcher SHALL issue one Gemini call per artist, looping over artists (not over series)

### Requirement: Verbatim Extraction Discipline

The searcher SHALL follow a two-step discipline to suppress hallucinated dates: a grounded step that extracts schedule values verbatim and retains the source URL, and a coercion step that only normalizes the extracted values into canonical date/time formats.

#### Scenario: Verbatim extract then coerce

- **WHEN** the searcher extracts a sales phase
- **THEN** schedule values SHALL be extracted verbatim from grounded content in the first step
- **AND** a source URL SHALL be retained for the extracted phase
- **AND** the second step SHALL only coerce those values into canonical formats, not invent new ones

#### Scenario: No actionable data found

- **WHEN** the grounding contains no usable sales-schedule information for the series
- **THEN** the searcher SHALL produce no sales phase for that series

### Requirement: Scheduled Sales-Phase Discovery Job

The system SHALL run a scheduled job that discovers sales phases for the upcoming series of followed artists and upserts them into storage, batching the search per artist.

#### Scenario: Scheduled execution batches by artist

- **WHEN** the discovery job runs on its schedule
- **THEN** it SHALL enumerate followed artists that have upcoming series
- **AND** for each artist, resolve the artist's official-site URL and invoke the sales-phase searcher once with that artist's known upcoming series
- **AND** upsert the resulting sales phases, converging on `(series_id, apply_start_time)`

#### Scenario: Artist without a usable official-site URL is skipped

- **WHEN** an artist has no official-site URL (or an empty one)
- **THEN** the job SHALL skip that artist without invoking the searcher (no grounding seed → no value), as a benign skip rather than an error

#### Scenario: Idempotent re-run

- **WHEN** the discovery job runs again over the same artists
- **THEN** previously discovered phases SHALL converge to the same rows by matching on `(series_id, apply_start_time)`
- **AND** no duplicate sales phases SHALL be created

#### Scenario: Empty extraction does not delete

- **WHEN** a run produces no phases for an artist (e.g. nothing new, grounding failure, or page unavailable)
- **THEN** the job SHALL NOT delete previously persisted phases for that artist's series (upsert-only semantics)

### Requirement: Event-Driven Announcement on New Phase

The system SHALL push an announcement when a newly discovered sales phase is persisted, reusing the existing discovery→event→push pipeline. This announcement is event-driven and distinct from the time-based reminders. The announcement SHALL be built per recipient and localized to the recipient's `preferred_language` (default `en`), consistent with the `sales-reminders` Notification Content requirement.

#### Scenario: New phase announced

- **WHEN** the discovery job persists a sales phase that did not previously exist
- **THEN** it SHALL publish a sales-phase-discovered event
- **AND** a consumer SHALL push an announcement to the followers of the performers of the phase's covered events, applying the existing hype-level filter

#### Scenario: Re-discovered phase is not re-announced

- **WHEN** the discovery job re-encounters an already-known phase (only updating its fields)
- **THEN** it SHALL NOT publish a new announcement for that phase

#### Scenario: Announcement copy localized per recipient

- **WHEN** the announcement is built for a recipient
- **THEN** its `title` and `body` SHALL be rendered in the recipient's `preferred_language`
- **AND** when the recipient has no `preferred_language` set, the copy SHALL default to `en`

