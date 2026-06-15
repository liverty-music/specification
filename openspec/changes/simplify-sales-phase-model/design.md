## Context

The sales-phase feature discovers ticket-sale windows for a series via a grounded Gemini search, persists them, announces newly found ones, and fires a multi-stage reminder ladder. The current model treats a phase as covering a *subset* of a series' events and relies on two fragile, LLM-derived signals for correctness:

1. **Covered-event resolution** — Step 1 extracts verbatim `covered_dates`, Step 2 matches those dates to known event indices. A miss silently drops a phase (the persistence guard requires at least one resolved covered event).
2. **Covered-event overlap + channel-compatibility** as the convergence key — re-discovered phases match an existing row by overlapping `event_ids` and a channel wildcard rule. Reclassification (`UNSPECIFIED`→`FAN_CLUB`) and coverage growth are handled here.

Two product decisions remove the justification for this machinery:
- **Audience is now an explicit fan signal.** Notifications target users with a `Tracking` ticket journey on the series' events, not followers filtered by covered-event proximity.
- **Notification content is already generic** (a title plus a `/series/{id}` link); the precise covered-event set is never surfaced to the fan.

With targeting and content both series-level, the covered-event refinement has no consumer, while remaining the single largest source of extraction inaccuracy. This design removes it and re-anchors identity on the one mandatory, stable attribute of a sale window: its application start time.

## Goals / Non-Goals

**Goals:**
- Make a sales phase a series-level record; eliminate covered-event resolution from the searcher and persistence.
- Use `(series_id, apply_start_time)` as the convergence signal — stable across `channel`/`sequence`/coverage drift, timezone-agnostic.
- Re-target announcement and reminder audiences to `Tracking` ticket journeys on the series' events.
- Preserve once-only announcement, once-only reminders, and reminder retention while milestones are pending.
- Reduce the LLM-accuracy-critical surface area to "is there a sale, and when does its application open?"

**Non-Goals:**
- No confidence tiering / recall-vs-precision split. Every persisted window (apply_start known) announces and schedules whatever reminder stages have timestamps. (Considered and dropped for simplicity.)
- No record deletion / GC. Completed phases are retained; reads filter by pending milestones.
- No change to notification content/copy or to the reminder stage set and timing.
- No "bootstrap" mechanism for fans who have not yet started tracking (accepted: fans track from the prior new-concert notification funnel).
- No per-leg / per-event targeting precision (explicitly removed).

## Decisions

### D1. A sales phase is series-level; drop `event_ids` and `anchor_event_id`

`SalesPhase` references only its `Series`. The `event_sales_phases` join table and `anchor_event_id` column are removed.

- **Why:** With tracking-based audience and generic content, covered events have no consumer. Removing them deletes the most error-prone extraction step and its persistence guard.
- **Alternative — keep covered events for future UI (event→phases reverse lookup):** rejected; the reverse lookup is satisfied via the series (an event's series → its phases), so no per-phase coverage is needed.

### D2. Convergence key = `(series_id, apply_start_time)`, matched in the application layer

The discovery upsert selects an existing phase by equal `series_id` and equal `apply_start_at`; found → update descriptive fields in place (silent), absent → insert + announce. `apply_start_at` is a `timestamptz` (an absolute instant), so the comparison is timezone-agnostic and works for non-JST events. `channel`, `sequence`, `method`, `provider_name`, and the other timestamps are descriptive, last-write-wins fields and never participate in identity. The surrogate `id` remains the only hard DB key and the stable handle reminders reference.

- **Why `apply_start_time`:** it is the only mandatory field (a phase without it is already dropped), it is the natural identity of a sales window, and it is immune to the reclassification/coverage drift that destabilized `channel`/`sequence` and covered-event overlap.
- **Alternative — JST-day truncation (`apply_jst_date`) to absorb time-precision drift:** rejected. Hardcoding `Asia/Tokyo` breaks overseas events, and it would collapse two same-day windows. Using the absolute instant directly is timezone-correct and keeps distinct same-day windows separate.
- **Alternative — DB `UNIQUE(series_id, apply_start_at)` constraint:** not required. The discovery job is a single sequential cron, so application-layer match (mirroring today's overlap-match pattern) is sufficient and keeps the tolerance tunable; a unique index may be added later as a safety net.
- **Accepted residual:** if the extracted start time drifts across runs (e.g. `7/1 10:00` one run, `7/1` the next), the window re-keys and re-announces. This is rare and the announcement is generic, so the cost is low.

### D3. Searcher stops resolving covered events; persistence guard requires only a known start

Remove the Step-1 `covered_dates` field and the Step-2 `covered_event_indices` resolution (`resolveCoveredEvents`, `earliestEventID`, the all-performances marker). A candidate is persisted iff `apply_start_time` is known; the "at least one resolved covered event" condition is dropped.

- **Why:** date→event matching was the dominant accuracy risk and now has no downstream use.

### D4. Audience = `Tracking` ticket journeys on the series' events

Both the announcement consumer and the reminder scan resolve recipients via a new reverse query: distinct users with a `TicketJourneyStatus = Tracking` journey on any event whose `series_id` is the phase's series. The existing proximity/follower/hype resolution (`ResolveSalesPhaseAudience` over covered-event performers) is removed from this path.

- **Why:** a `Tracking` journey is an explicit "notify me about this sale" signal — more precise than geographic proximity and independent of covered-event accuracy. Geographic relevance was already applied upstream when the fan was notified of the concert and chose to track it.
- **Status filter:** only `Tracking` (status 1). Fans in later lifecycle states (`Applied`/`Paid`/…) are not re-targeted by sales-phase notifications for that series. (Confirmed scope decision.)
- **Alternative — keep a follower/proximity fallback for the first announcement (bootstrap):** out of scope by decision; accepted that a sale announced before any fan tracks reaches no one until a fan tracks and later phases/reminders catch them.

### D5. Upsert-only, retain while pending, no GC

An empty or failed extraction never deletes rows (avoids losing reminder-bearing phases and avoids re-insert announcement storms). A phase is retained as long as any milestone is pending; the reminder scan already filters via `GREATEST(apply_start, apply_end, lottery_result) >= now - margin`. No deletion/GC job is introduced.

- **Why:** correctness does not depend on physical cleanup; read-side filtering already hides completed phases. (Simplicity decision.)

## Risks / Trade-offs

- **Start-time drift re-announces a window** → Accepted; rare and low-cost (generic announcement). A later `UNIQUE`/tolerance refinement can mitigate if observed.
- **Two genuinely distinct sales of one series sharing the exact same `apply_start_at`** collapse into one row (last-write-wins) → Extremely rare; generic notification + series link means the fan still sees both on the official page.
- **Bootstrap gap: a sale announced before anyone tracks reaches no audience** → Accepted by decision; the new-concert notification funnel seeds tracking, and reminders/later phases recover the fan.
- **Breaking proto change** (`SalesPhase` loses `event_ids`/`anchor_event_id`) → Coordinated via the standard specification → BSR release → backend/frontend upgrade flow; no consumer reads covered events for behavior today.
- **Reminder once-only key references the surrogate `id`** → `id` stays stable because convergence updates in place on `apply_start` match; drift that mints a new `id` only risks re-announcing, not duplicate reminders (the new phase's own once-only log governs it).

## Migration Plan

1. **specification**: update `sales-phase`, `sales-phase-discovery`, `sales-reminders` specs (delta files in this change) and the `SalesPhase` proto (drop `event_ids`, `anchor_event_id`); open PR; merge; cut a Release to trigger BSR generation.
2. **backend** (prepared in parallel, pushed after BSR gen): drop covered-event extraction/resolution in the searcher; change `Upsert` to `(series_id, apply_start_at)` match and stop writing `event_sales_phases`; remove `ReplaceCoveredEvents`; replace `ResolveSalesPhaseAudience` with the `Tracking`-journey lookup; add `TicketJourneyRepository` reverse query.
3. **DB migration**: drop `event_sales_phases`; drop `sales_phases.anchor_event_id`. Existing `sales_phases` rows keep `series_id` + `apply_start_at` and remain valid under the new convergence key.
4. **Rollback**: revert backend + proto; the dropped join table/column would need restoration from migration history if rolled back after deploy — treat as forward-only once released.

## Open Questions

- Should a `UNIQUE(series_id, apply_start_at)` index be added now as a concurrency/duplicate safety net, or deferred until drift is observed in production? (Leaning defer.)
