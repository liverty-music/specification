## Why

The current sales-phase model binds each phase to a *subset* of a series' events (`event_ids` / `anchor_event_id`) and converges re-discovered phases via covered-event overlap plus a channel-compatibility rule. This makes the most fragile part of the LLM pipeline — matching verbatim Japanese sale dates back to specific events, and keeping `channel`/`sequence` stable across runs — load-bearing for both deduplication and notification targeting. The result is genuine accuracy anxiety: a date-matching miss can drop a phase entirely (a fan misses a sale), and a channel reclassification can spawn a duplicate announcement.

Because the audience is now resolved from an explicit fan signal (a `Tracking` ticket journey) rather than covered-event proximity, the covered-event refinement has no remaining consumer. Removing it lets the whole feature converge on the one stable, mandatory attribute of a sales window — its application start time — and collapses the accuracy-critical surface area.

## What Changes

- **BREAKING** Remove the covered-events relationship from `SalesPhase`: drop `event_ids` and `anchor_event_id`. A sales phase belongs to a `Series` and applies to the series as a whole.
- Change phase identity/convergence to **same `series_id` + same `apply_start_time`** (an absolute instant; timezone-agnostic so non-JST events work). `channel`, `sequence`, `method`, `provider_name`, and the other timestamps become purely descriptive, last-write-wins fields — never identity.
- Drop the covered-event extraction step from the Gemini searcher (no more `covered_dates` / `covered_event_indices` resolution). Phases are persisted whenever `apply_start_time` is known.
- Change the discovery upsert from covered-event overlap + channel-compatibility matching to a plain `(series_id, apply_start_time)` match: found → update in place (silent), absent → insert + announce. Keep upsert-only semantics (an empty extraction never deletes existing rows).
- Re-target both the **announcement** and the **reminder** audience to users who have a `Tracking` ticket journey on **any event of the phase's series**. Remove follower/proximity/hype resolution from the sales-phase path.
- Keep retaining a phase while any milestone is still pending (reminders unchanged in spirit); **no record deletion / GC** is introduced — reads filter by pending milestones.
- **BREAKING** Drop the `event_sales_phases` join table and the `anchor_event_id` column. Convergence on `(series_id, apply_start_at)` is enforced in the application layer; a `UNIQUE` index may be added later as a safety net.

## Capabilities

### New Capabilities
<!-- None: this change modifies existing sales-phase capabilities only. -->

### Modified Capabilities
- `sales-phase`: SalesPhase entity drops `event_ids`/`anchor_event_id`; identity/convergence moves from covered-event overlap to `(series_id, apply_start_time)`; persistence guard drops the "at least one covered event" condition (only a known start is required); database schema removes the join table and anchor column.
- `sales-phase-discovery`: searcher stops extracting/resolving covered dates; discovery upsert matches on `(series_id, apply_start_time)`; announcement audience resolves from `Tracking` ticket journeys on the series' events instead of followers of covered-event performers.
- `sales-reminders`: reminder audience resolves from `Tracking` ticket journeys on the series' events (drops the covered-event/follower/hype resolution and the per-leg targeting scenario); once-only delivery keyed by `(user_id, sales_phase_id, stage)` is retained; notification content's `url` fallback changes from the concert detail to the series detail (no single covered concert exists under the series-level model).

## Impact

- **Protobuf (specification)**: `liverty_music.entity.v1.SalesPhase` removes `event_ids` and `anchor_event_id` — a breaking schema change requiring a new BSR release.
- **Backend**: `entity.SalesPhase`/`SalesPhaseCandidate` (drop covered fields); `SalesPhaseRepository.Upsert` (apply_start match, drop overlap query + `event_sales_phases` writes + `ReplaceCoveredEvents`); Gemini `sales_phase_searcher` (drop Step-1 `covered_dates` and Step-2 index resolution); `ResolveSalesPhaseAudience` (replace covered-event/proximity/follower/hype with a `Tracking`-journey lookup); new `TicketJourneyRepository` reverse query (users tracking any event in a series).
- **Database migration**: drop `event_sales_phases` table and `sales_phases.anchor_event_id`. (Convergence is application-layer; no uniqueness index is added by this change.)
- **No frontend behavior change** to notification content (already generic + series link); fans must have a `Tracking` journey to be notified (explicit-intent funnel).
