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

### Requirement: Stable, Collision-Free Phase Identity

The system SHALL assign each sales phase a stable upsert identity that (a) resolves to the same row when the same real phase is re-extracted, and (b) never collapses two distinct real phases of a series into one row. The identity SHALL NOT depend solely on `(series_id, channel, sequence)`, because both `channel` and `sequence` may take their default values (`channel = UNSPECIFIED`, `sequence = 0`) for phases the searcher cannot classify; keying on those alone would let one real phase overwrite another (silent data loss).

The `stable_key` SHALL be composed of `(series_id, channel, sequence, anchor_event_id)`, where `anchor_event_id` is the earliest (by date) event the phase covers. `anchor_event_id` is the primary distinguisher between sibling phases that share `channel`/`sequence` — most importantly per-leg phases (first-half vs. second-half), which differ precisely in which events they cover. Because event IDs are immutable, the anchor is stable across re-discovery even as the phase's timestamps are corrected, and it does not rely on volatile fields like `apply_start_time`.

The `stable_key` SHALL be frozen at first insert and never recomputed or mutated; the upsert SHALL match on it, and last-write-wins updates to mutable fields (`apply_end_time`, `lottery_result_time`, `payment_deadline_time`, `provider_name`, `url`, and the covered-event set) SHALL NOT change it.

#### Scenario: Re-extraction converges to one row

- **WHEN** the same real sales phase is extracted again with updated details
- **THEN** it SHALL resolve to the existing row via its frozen `stable_key`
- **AND** later writes of `apply_start_time`, `apply_end_time`, `lottery_result_time`, `payment_deadline_time`, `provider_name`, and `url` SHALL take precedence (last-write-wins) without changing `stable_key`

#### Scenario: Confirming a previously-null field does not duplicate

- **WHEN** a phase first persisted with a null `apply_end_time` is re-discovered with a confirmed `apply_end_time`
- **THEN** it SHALL match the existing row via its frozen `stable_key` and update it in place
- **AND** it SHALL NOT insert a new row or re-fire the `SALES_PHASE.discovered` announcement

#### Scenario: Two unclassifiable phases do not collide

- **WHEN** a series has two distinct sales phases that both carry `channel = UNSPECIFIED` but cover different events
- **THEN** they SHALL receive distinct identities via their different `anchor_event_id`
- **AND** both SHALL be persisted as separate rows rather than one overwriting the other

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
- **AND** it SHALL store method, channel, provider_name, sequence, the four nullable timestamps, and url
- **AND** it SHALL store an immutable `stable_key` (set once at insert, never updated) and enforce uniqueness on `(series_id, stable_key)`, per the Stable, Collision-Free Phase Identity requirement (not on `(series_id, channel, sequence)` when `channel`/`sequence` are defaulted)
- **AND** the covered-events relationship SHALL be stored in an `event_sales_phases` join table keyed by `(sales_phase_id, event_id)`, each `event_id` referencing an event of the phase's series
- **AND** the existing `ticket_emails` table SHALL NOT be modified by this change
