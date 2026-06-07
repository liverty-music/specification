## ADDED Requirements

### Requirement: SalesPhase Entity

The system SHALL define a `SalesPhase` entity representing one ticket-sales opportunity. Each sales phase belongs to a `Series` (the tour) and covers a specific subset of that series' events, because a tour can announce distinct phases for different legs (e.g. first-half dates vs. second-half dates) rather than one phase applying uniformly to every date.

#### Scenario: SalesPhase data model

- **WHEN** a sales phase is represented
- **THEN** it SHALL include `id` (SalesPhaseId), `series_id` (SeriesId), `method` (SalesMethod), `channel` (SalesChannel), `provider_name` (string), and `sequence` (int32)
- **AND** it SHALL include the set of events it covers as `event_ids` (repeated EventId, at least one), all belonging to `series_id`
- **AND** it SHALL include `apply_start_time` (Timestamp, required — a phase is never persisted without it) and the nullable timeline fields `apply_end_time`, `lottery_result_time`, `payment_deadline_time`
- **AND** it SHALL include a nullable `url` field reusing the `Url` value object
- **AND** `series_id` SHALL be the only required entity reference; `apply_start_time` and at least one covered event are also required for persistence

#### Scenario: Phase covers a subset of the series' events

- **WHEN** a tour announces separate sales phases for different legs (e.g. first-half and second-half dates)
- **THEN** each `SalesPhase` SHALL cover only the events of its leg via `event_ids`
- **AND** an `Event` SHALL be resolvable to the phases that cover it
- **AND** a standalone concert (series of one event) SHALL have its phases cover that single event

### Requirement: SalesPhase Identity

The system SHALL identify each sales phase with a `SalesPhaseId` value object wrapping a UUID.

#### Scenario: SalesPhaseId format

- **WHEN** a `SalesPhaseId` is represented
- **THEN** its `value` SHALL be a valid UUID string

### Requirement: Sales Method and Channel Classification

The system SHALL classify each sales phase by `method` and `channel` as orthogonal dimensions, plus an ordinal `sequence`, rather than a single conflated tier enum.

#### Scenario: SalesMethod values

- **WHEN** a sales method is represented
- **THEN** it SHALL be one of `UNSPECIFIED`, `LOTTERY`, or `FIRST_COME`
- **AND** `UNSPECIFIED` SHALL be permitted to mean "not yet determined"

#### Scenario: SalesChannel values

- **WHEN** a sales channel is represented
- **THEN** it SHALL be one of `UNSPECIFIED`, `FAN_CLUB`, `OFFICIAL`, `PLAYGUIDE`, `CREDIT_CARD`, `MOBILE_CARRIER`, or `GENERAL`

#### Scenario: Sequence captures round ordinal

- **WHEN** a series has multiple rounds (earliest, first, second, …)
- **THEN** the round ordering SHALL be expressed via `sequence` (0=earliest, 1=first, 2=second, …)
- **AND** adding further rounds SHALL NOT require any schema change

### Requirement: Timeline Fields Are Nullable Except the Start

The system SHALL require `apply_start_time` on every persisted phase (see Persist Only Phases With a Known Start) and treat the remaining timeline fields (`apply_end_time`, `lottery_result_time`, `payment_deadline_time`) as nullable, where null means "not yet announced". The row's existence signals the phase is happening; no separate to-be-determined flag is required.

#### Scenario: Start known, later milestones not yet announced

- **WHEN** a phase has a known `apply_start_time` but its close / result / payment dates are not yet announced
- **THEN** the `SalesPhase` SHALL exist with `apply_start_time` set and the other timeline fields left null

### Requirement: Best-Effort Stable Phase Identity

The system SHALL give each sales phase a surrogate `id` (UUID) as its only hard identity (the handle referenced by reminders). Re-extractions of the same real phase SHALL converge to the same row on a best-effort basis. Because the source data is LLM-extracted and incrementally resolved — coverage grows over runs and `channel`/`sequence` may reclassify (e.g. `UNSPECIFIED`/`0` → `FAN_CLUB`/`1`) — no field is perfectly stable.

The primary match signal SHALL be **same `series_id` + covered-event overlap**. Event IDs are immutable and overlap survives both incremental coverage growth and `channel`/`sequence` reclassification, so a reclassified or coverage-grown phase converges to its existing row instead of re-keying into a duplicate. `channel`, `sequence`, and a frozen `anchor_event_id` are recorded for display and used **only** to keep clearly-different sales (e.g. distinct rounds) separate when their coverage overlaps; they SHALL NOT be hard-equality match keys. All non-key fields — `apply_start_time`, the other timestamps, `provider_name`, `url`, and the covered-event set — are last-write-wins on a matched row.

This stance favors robust convergence; the accepted residual is the rare case of two genuinely distinct phases that share covered events and are indistinguishable by `channel`/`sequence`. Such a pair would be **conflated — one phase's data silently overwritten via last-write-wins (data loss)**, not merely duplicated. This is accepted as a known limitation of fuzzy extracted data and minimized by `channel`/`sequence` disambiguation.

#### Scenario: Re-extraction converges to one row

- **WHEN** the same real sales phase is extracted again with updated details (possibly reclassified channel/sequence or grown coverage)
- **THEN** it SHALL match the existing row by same `series_id` and covered-event overlap
- **AND** its fields (`apply_start_time`, the other timestamps, `provider_name`, `url`, covered-event set) SHALL be updated last-write-wins without inserting a duplicate or re-firing the announcement

#### Scenario: Reclassification does not duplicate

- **WHEN** a phase first persisted as `(channel = UNSPECIFIED, sequence = 0)` is re-extracted as `(FAN_CLUB, 1)` with overlapping coverage
- **THEN** covered-event overlap SHALL still match the existing row (channel/sequence are not hard-equality keys)
- **AND** it SHALL update in place rather than insert a duplicate or re-fire `SALES_PHASE.discovered`

#### Scenario: Per-leg phases stay separate

- **WHEN** a series has a first-half phase and a second-half phase with disjoint covered events
- **THEN** their non-overlapping coverage SHALL keep them as separate rows
- **AND** the residual risk is over-matching two genuinely distinct phases that share coverage and channel/sequence — accepted as a rare known limitation whose failure is silent conflation (data loss), minimized by channel/sequence disambiguation

### Requirement: Persist Only Phases With a Known Start and Coverage

The system SHALL persist a `SalesPhase` only when both (a) its `apply_start_time` is known and (b) at least one covered event has been resolved to a known `event_id`. A phase whose start is unknown is not actionable for a fan and cannot anchor a reminder; a phase with no resolvable covered event has no `anchor_event_id` and no audience. Such phases SHALL be dropped at search time.

#### Scenario: Phase without a known start is dropped

- **WHEN** an extracted phase has no concrete `apply_start_time`
- **THEN** the system SHALL NOT persist a `SalesPhase` for it

#### Scenario: Phase with no resolvable covered event is dropped

- **WHEN** none of an extracted phase's covered dates resolve to a known event of the series
- **THEN** the system SHALL NOT persist a `SalesPhase` for it (it may resolve on a later run once the events are discovered)

#### Scenario: Phase with a known start and coverage is persisted

- **WHEN** an extracted phase has a concrete `apply_start_time` and at least one resolved covered event
- **THEN** the system SHALL persist it even if `apply_end_time`, `lottery_result_time`, or `payment_deadline_time` are still null

### Requirement: SalesPhase Database Schema

The system SHALL store sales phases in a `sales_phases` table.

#### Scenario: Table structure

- **WHEN** the `sales_phases` table is created
- **THEN** it SHALL have an `id` UUID primary key and a `series_id` foreign key referencing series
- **AND** it SHALL store method, channel, provider_name, sequence, `apply_start_at` (NOT NULL), the three nullable timestamps (`apply_end_at`, `lottery_result_at`, `payment_deadline_at`), and url
- **AND** the surrogate `id` SHALL be the only uniqueness constraint; it SHALL store an immutable `anchor_event_id` (set once at insert as a representative, never recomputed) but SHALL NOT impose a unique constraint over `(series_id, channel, sequence)` or the anchor, since convergence is the application-level best-effort overlap match defined in Best-Effort Stable Phase Identity
- **AND** the covered-events relationship SHALL be stored in an `event_sales_phases` join table keyed by `(sales_phase_id, event_id)`, each `event_id` referencing an event of the phase's series
- **AND** the existing `ticket_emails` table SHALL NOT be modified by this change
