# sales-phase-discovery Specification

## Purpose
TBD - created by archiving change add-sales-phase-timeline. Update Purpose after archive.
## Requirements
### Requirement: Dedicated Sales-Phase Searcher

The system SHALL provide a sales-phase searcher that is separate from the concert searcher, because the concert searcher's grounding (the artist's official site) does not contain ticket sales schedules. The sales-phase searcher SHALL take an artist name and a series title as input and extract that series' sales phases as series-level records. It SHALL NOT resolve which individual events a phase covers.

#### Scenario: Search sales phases for a series

- **WHEN** the searcher is invoked with an artist name and a series title
- **THEN** it SHALL issue a Gemini call grounded to find that series' ticket sales information
- **AND** it SHALL return the extracted sales phases for that series as series-level records

#### Scenario: No covered-event resolution

- **WHEN** the searcher extracts a sales phase for a series
- **THEN** it SHALL NOT extract per-phase covered dates nor resolve them to the series' `event_id`s
- **AND** each extracted phase SHALL carry only its series-level attributes (`apply_start_time` and the descriptive fields)

#### Scenario: One call per series

- **WHEN** discovery processes multiple series
- **THEN** the searcher SHALL issue one Gemini call per series, looping over the series

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

The system SHALL run a scheduled job that discovers sales phases for the upcoming series of followed artists and upserts them into storage.

#### Scenario: Scheduled execution

- **WHEN** the discovery job runs on its schedule
- **THEN** it SHALL enumerate the series of followed artists that have upcoming events
- **AND** invoke the sales-phase searcher for each such series
- **AND** upsert the resulting sales phases

#### Scenario: Idempotent re-run

- **WHEN** the discovery job runs again over the same series
- **THEN** previously discovered phases SHALL converge to the same rows by matching on `(series_id, apply_start_time)`
- **AND** no duplicate sales phases SHALL be created

#### Scenario: Empty extraction does not delete

- **WHEN** a run produces no phases for a series (e.g. grounding failure or page unavailable)
- **THEN** the job SHALL NOT delete previously persisted phases for that series (upsert-only semantics)

### Requirement: Event-Driven Announcement on New Phase

The system SHALL push an announcement when a newly discovered sales phase is persisted, reusing the existing discovery→event→push pipeline. This announcement is event-driven and distinct from the time-based reminders. The announcement SHALL be built per recipient and localized to the recipient's `preferred_language` (default `en`), consistent with the `sales-reminders` Notification Content requirement.

#### Scenario: New phase announced to tracking fans

- **WHEN** the discovery job persists a sales phase that did not previously exist
- **THEN** it SHALL publish a sales-phase-discovered event
- **AND** a consumer SHALL push an announcement to the users who have a `Tracking` ticket journey on any event of the phase's series
- **AND** it SHALL NOT resolve the audience from covered-event performers, follower lists, or hype-level proximity

#### Scenario: Re-discovered phase is not re-announced

- **WHEN** the discovery job re-encounters an already-known phase (only updating its fields)
- **THEN** it SHALL NOT publish a new announcement for that phase

#### Scenario: Announcement copy localized per recipient

- **WHEN** the announcement is built for a recipient
- **THEN** its `title` and `body` SHALL be rendered in the recipient's `preferred_language`
- **AND** when the recipient has no `preferred_language` set, the copy SHALL default to `en`

### Requirement: Play-guide sales are classified as プレイガイド even when general

When a sales phase is conducted through a named third-party play guide (for example e+ / イープラス, ローチケ, チケットぴあ, CN Playguide), the grounded extraction step SHALL classify its channel as `プレイガイド` and record the guide in `provider_name`, even when the sale is a general (non-membership) on-sale. The `一般` channel SHALL be reserved for a general on-sale that is not tied to a named play guide.

#### Scenario: General on-sale sold via a named play guide

- **WHEN** a general on-sale for a series is sold through イープラス
- **THEN** the phase channel SHALL be `プレイガイド`
- **AND** `provider_name` SHALL be the guide name (e.g. `イープラス`)
- **AND** the channel SHALL NOT be `一般`

#### Scenario: General on-sale with no named guide

- **WHEN** a general on-sale is a direct sale on the official site with no third-party play guide named
- **THEN** the phase channel SHALL be `一般`

### Requirement: Lottery phases extract the application deadline and result date when published

For a `抽選` (lottery) phase, the grounded extraction step SHALL extract the application deadline (`apply_end`) and the result-announcement date (`lottery_result`) from the ticket page when they are published alongside the application window, and SHALL leave them empty only when they are genuinely absent — never guessed.

#### Scenario: Lottery with a published deadline and result date

- **WHEN** a `抽選` phase's page publishes an application window with a deadline and a result-announcement date
- **THEN** the extracted phase SHALL include both `apply_end` and `lottery_result`

#### Scenario: Lottery with no published result date

- **WHEN** a `抽選` phase's page does not publish a result-announcement date
- **THEN** `lottery_result` SHALL be left empty rather than guessed

