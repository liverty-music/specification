# Sales Phase

## Purpose

TBD - created by archiving change add-sales-phase-timeline. Update Purpose after archive.

## Requirements

### Requirement: SalesPhase represents one ticket-sales opportunity

The system SHALL define a `SalesPhase` entity representing one ticket-sales opportunity. Each sales phase belongs to a `Series` (the tour) and applies to the series as a whole; it does NOT track a per-event coverage subset. A series-level model is sufficient because notification targeting is driven by an explicit fan signal (a `Tracking` ticket journey on the series' events) and notification content is generic (a series link), so the precise set of covered dates is never consumed.

#### Scenario: SalesPhase data model

- **WHEN** a sales phase is represented
- **THEN** it SHALL include `id` (SalesPhaseId), `series_id` (SeriesId), `method` (SalesMethod), `channel` (SalesChannel), `provider_name` (string), and `sequence` (int32)
- **AND** it SHALL include `apply_start_time` (Timestamp, required — a phase is never persisted without it) and the nullable timeline fields `apply_end_time`, `lottery_result_time`, `payment_deadline_time`
- **AND** it SHALL include a nullable `url` field reusing the `Url` value object
- **AND** `series_id` SHALL be the only required entity reference; `apply_start_time` is also required for persistence
- **AND** it SHALL NOT include an `event_ids` covered-event set nor an `anchor_event_id`

#### Scenario: Phase applies to the whole series

- **WHEN** a tour announces a sales phase
- **THEN** the `SalesPhase` SHALL apply to its `series_id` as a whole, with no per-event coverage subset
- **AND** the phases relevant to an `Event` SHALL be resolvable via that event's `series_id` (an event → its series → the series' phases), not via a per-phase covered-event list
- **AND** a standalone concert (series of one event) SHALL have its phases belong to that single-event series

### Requirement: SalesPhaseId is a UUID value object

The system SHALL identify each sales phase with a `SalesPhaseId` value object wrapping a UUID.

#### Scenario: SalesPhaseId format

- **WHEN** a `SalesPhaseId` is represented
- **THEN** its `value` SHALL be a valid UUID string

### Requirement: SalesMethod and SalesChannel are orthogonal classifications

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

### Requirement: Only apply_start_time is required on a sales phase

The system SHALL require `apply_start_time` on every persisted phase (see Persist Only Phases With a Known Start) and treat the remaining timeline fields (`apply_end_time`, `lottery_result_time`, `payment_deadline_time`) as nullable, where null means "not yet announced". The row's existence signals the phase is happening; no separate to-be-determined flag is required.

#### Scenario: Start known, later milestones not yet announced

- **WHEN** a phase has a known `apply_start_time` but its close / result / payment dates are not yet announced
- **THEN** the `SalesPhase` SHALL exist with `apply_start_time` set and the other timeline fields left null
