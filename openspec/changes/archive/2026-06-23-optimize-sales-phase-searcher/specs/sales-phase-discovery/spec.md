## MODIFIED Requirements

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
