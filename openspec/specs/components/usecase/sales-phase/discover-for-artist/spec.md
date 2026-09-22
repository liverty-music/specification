# Discover For Artist

## Purpose

Discovers and tracks the ticket sales-phase timeline for an artist's concerts, extracting details such as lottery deadlines and result dates verbatim from sources, converging repeated discoveries on a consistent phase, and running on a schedule.

## Requirements

### Requirement: Re-discovered sales phases converge to the same phase

The system SHALL give each sales phase a surrogate `id` (UUID) as its only hard identity (the handle referenced by reminders). Re-extractions of the same real phase SHALL converge to the same row on a best-effort basis. Because the source data is LLM-extracted, `channel`, `sequence`, `provider_name`, and the later timestamps may reclassify or be refined across runs — so none of those fields is a stable identity.

The primary match signal SHALL be **same `series_id` + same `apply_start_time`**. `apply_start_time` is the only mandatory field and the natural identity of a sales window; it is immune to the `channel`/`sequence` reclassification that would otherwise spawn duplicates. It is stored as an absolute instant (timezone-agnostic) so the match is correct for non-JST events. `channel`, `sequence`, `method`, `provider_name`, the other timestamps, and `url` are descriptive, last-write-wins fields and SHALL NOT participate in identity. The match SHALL be performed in the application layer (the discovery job is a single sequential runner), with the surrogate `id` as the only hard database key.

The accepted residual is that (a) if the extracted `apply_start_time` drifts across runs the window re-keys and re-announces (rare; the announcement is generic), and (b) two genuinely distinct sales of one series sharing the exact same `apply_start_time` collapse into one row via last-write-wins (extremely rare).

#### Scenario: Re-extraction converges to one row

- **WHEN** the same real sales phase is extracted again with updated details (possibly reclassified `channel`/`sequence` or newly filled timestamps)
- **THEN** it SHALL match the existing row by same `series_id` and same `apply_start_time`
- **AND** its descriptive fields (`method`, `channel`, `sequence`, `provider_name`, the other timestamps, `url`) SHALL be updated last-write-wins without inserting a duplicate or re-firing the announcement

#### Scenario: Reclassification does not duplicate

- **WHEN** a phase first persisted as `(channel = UNSPECIFIED, sequence = 0)` is re-extracted as `(FAN_CLUB, 1)` with the same `apply_start_time`
- **THEN** the `(series_id, apply_start_time)` match SHALL still find the existing row (channel/sequence are not match keys)
- **AND** it SHALL update in place rather than insert a duplicate or re-fire `SALES_PHASE.discovered`

#### Scenario: Distinct windows stay separate

- **WHEN** a series has two sales phases with different `apply_start_time` values (e.g. an FC presale and a later general on-sale)
- **THEN** their differing `apply_start_time` SHALL keep them as separate rows

### Requirement: Only persist a discovered phase with a known start

The system SHALL persist a `SalesPhase` only when its `apply_start_time` is known. A phase whose start is unknown is not actionable for a fan and cannot anchor a reminder. There is NO covered-event condition: a known start is the sole persistence requirement. Such start-less phases SHALL be dropped at search time.

#### Scenario: Phase without a known start is dropped

- **WHEN** an extracted phase has no concrete `apply_start_time`
- **THEN** the system SHALL NOT persist a `SalesPhase` for it

#### Scenario: Phase with a known start is persisted

- **WHEN** an extracted phase has a concrete `apply_start_time`
- **THEN** the system SHALL persist it even if `apply_end_time`, `lottery_result_time`, or `payment_deadline_time` are still null

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
