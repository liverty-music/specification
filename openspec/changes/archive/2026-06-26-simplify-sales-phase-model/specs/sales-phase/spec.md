## MODIFIED Requirements

### Requirement: SalesPhase Entity

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

### Requirement: Best-Effort Stable Phase Identity

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

### Requirement: SalesPhase Database Schema

The system SHALL store sales phases in a `sales_phases` table.

#### Scenario: Table structure

- **WHEN** the `sales_phases` table is created
- **THEN** it SHALL have an `id` UUID primary key and a `series_id` foreign key referencing series
- **AND** it SHALL store method, channel, provider_name, sequence, `apply_start_at` (NOT NULL), the three nullable timestamps (`apply_end_at`, `lottery_result_at`, `payment_deadline_at`), and url
- **AND** the surrogate `id` SHALL be the only hard uniqueness constraint; convergence on `(series_id, apply_start_at)` is the application-level match defined in Best-Effort Stable Phase Identity, not a database unique constraint (a `UNIQUE (series_id, apply_start_at)` index MAY be added later as a safety net)
- **AND** it SHALL NOT store an `anchor_event_id` column nor an `event_sales_phases` join table
- **AND** the existing `ticket_emails` table SHALL NOT be modified by this change

## REMOVED Requirements

### Requirement: Persist Only Phases With a Known Start and Coverage

**Reason**: The covered-event coverage condition is removed along with the covered-events model. A phase is now persisted on a known start alone; replaced by "Persist Only Phases With a Known Start".

**Migration**: Existing `sales_phases` rows remain valid — they already carry `series_id` and `apply_start_at`. The `event_sales_phases` join table and `anchor_event_id` column are dropped; no phase is re-evaluated for coverage.

## ADDED Requirements

### Requirement: Persist Only Phases With a Known Start

The system SHALL persist a `SalesPhase` only when its `apply_start_time` is known. A phase whose start is unknown is not actionable for a fan and cannot anchor a reminder. There is NO covered-event condition: a known start is the sole persistence requirement. Such start-less phases SHALL be dropped at search time.

#### Scenario: Phase without a known start is dropped

- **WHEN** an extracted phase has no concrete `apply_start_time`
- **THEN** the system SHALL NOT persist a `SalesPhase` for it

#### Scenario: Phase with a known start is persisted

- **WHEN** an extracted phase has a concrete `apply_start_time`
- **THEN** the system SHALL persist it even if `apply_end_time`, `lottery_result_time`, or `payment_deadline_time` are still null
