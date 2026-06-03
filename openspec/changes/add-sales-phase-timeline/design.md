## Context

New-concert discovery and follower push notifications already exist (`auto-concert-discovery` + Web Push). What is missing is any objective record of the **ticket sales timeline**: application open/close, lottery-result announcement, and payment deadline. `TicketJourney` only holds a fan's self-reported status; it carries no schedule.

Findings from codebase exploration that shape this design:

1. The existing Gemini concert searcher (`internal/infrastructure/gcp/gemini/searcher.go`) grounds only on the artist's **official site** plus brand-domain Google Search. Sales schedules live on play-guide platforms (e+, ぴあ, ローチケ) and are essentially absent from that grounding. So sales-phase extraction needs a **separate, purpose-built searcher**, not an extension of the concert searcher.
2. **Series semantics depend on tour bundling.** A sales phase (e.g. FC presale) is announced per tour, but a tour can split into **separate phases per leg** (first-half dates vs. second-half dates). Representing that requires a tour to be **one `Series` containing multiple `Event`s**. Today `concert_creation_uc.go` derives `seriesID` from `venue + local_date` (one Event per Series, `SERIES_TYPE_SINGLE` fallback); folding tour dates into a single tour-level `Series` is the `auto-discovery-series-grouping` capability, **handled concurrently in a separate session**. This design assumes that tour-level `Series` as its premise.
3. **Two notification types, different triggers.** Announcing a newly discovered phase reacts to an event that happens now (discovery) → event-driven. Reminding "24h before the deadline" reacts to the clock crossing a future threshold, which emits no event → requires a time-based trigger. There is **no delayed/scheduled-message capability** (NATS JetStream fires immediately), so the time-based reminders follow the established periodic-scan CronJob pattern (`concert-discovery`).

A fourth constraint is product-level: the `ticket-email-import` feature's ingestion entry point (PWA Share Target from the Android Gmail app) no longer works because Gmail removed its share action. Email is therefore frozen for now, leaving the sales-phase searcher as the sole writer of sales-schedule data.

## Goals / Non-Goals

**Goals:**
- Model the ticket sales timeline as a first-class `SalesPhase` entity that belongs to a `Series` (tour) and **covers a subset of that tour's events** (so first-half / second-half phases are distinct).
- Populate it automatically via a dedicated Gemini searcher that takes artist + tour title, extracts the tour's sales phases **and the dates each phase covers**.
- Push an **event-driven announcement** when a new phase is discovered, and **time-based reminders** (application open, 24h before close, 1h before close, lottery-result day) before each milestone, to the followers of the performers of each phase's covered events, reusing existing Web Push infrastructure.
- Cleanly disable the unusable email-import entry point without deleting its code.

**Non-Goals:**
- Tour-level `Series` grouping itself (`auto-discovery-series-grouping`) — built in a separate, concurrent session. This design **assumes** it; it does not implement it.
- A **payment-deadline reminder stage**. `SalesPhase.payment_deadline_time` is captured now (objectively knowable for pattern A) but no reminder fires on it: a blanket "payment due" push to all followers is wrong because only lottery winners pay, and win/loss status (funnel ③) is out of scope. It becomes a stage once win/loss gating exists.
- Importing lottery win/loss results (private inbox data) — funnel stage ③. Deferred to an email-revival phase.
- `TicketJourney`↔`SalesPhase` linkage (`phase_id`).
- Per-user first-come (conbini) payment deadlines (pattern B).
- The F "Next Action" dashboard and C merch features.
- Refactoring frozen `TicketEmail` storage onto `SalesPhase`.

## Decisions

### Decision 1: `SalesPhase` belongs to a `Series` (tour) and covers a subset of its events (M:N)
```
Series ──1:N──> SalesPhase ──M:N──> Event   (event_sales_phases join)
```
- `SalesPhase.series_id` (FK) — the tour the phase belongs to. Tour-level `Series` is provided by the concurrent `auto-discovery-series-grouping` session.
- `SalesPhase` carries the set of events it sells (`repeated EventId event_ids`), persisted as an `event_sales_phases (sales_phase_id, event_id)` join. This lets one tour have **distinct phases per leg** — e.g. "first-half FC presale" covering dates 1–5 and "second-half FC presale" covering dates 6–10 — rather than one phase implicitly applying to every date.
- An `Event` therefore references the phases that cover it (the join read from the Event side), so concert detail for a given date can list exactly the applicable phases.
- The fan's per-date result stays Event-scoped on `TicketJourney` (unchanged): objective schedule at phase/tour grain, subjective result at Event grain.
- Standalone concert = `Series` of one Event; its phases cover that single event.
- **Alternative considered**: phase applies to the whole Series implicitly (no event join). Rejected — cannot express per-leg phases, which are common.
- **Alternative considered**: Event-scoped `SalesPhase` (no Series). Rejected — duplicates a tour-wide phase across every date and loses the tour grouping.

### Decision 2: Dedicated sales-phase searcher, separate from concert search
Concert grounding (official site) does not contain sales schedules. The new searcher takes `artist name + tour (series) title`, issues one Gemini call per series, and follows the existing two-step discipline: Step 1 grounded **verbatim** extraction (keep `source_url`), Step 2 JSON coercion of dates.

**Coverage resolution (how a phase links to events).** The discovery job loads the series' candidate events (`ConcertRepository.ListByArtist(..., upcomingOnly)` filtered to the series → `event_id` + date + venue + admin_area) and injects them, index-tagged, into Step 2 — reusing the established `step2InputEvent`/`step2OutputEvent`/`byIndex` merge mechanism the concert searcher already uses. Step 2 returns, per phase, the indices of the candidate events it covers; Go resolves indices → `event_id`s. Because the candidate set is one tour's handful of dates, the match (e.g. "東名阪公演" → those events) is a small, bounded problem. A date that resolves to several events (two Tokyo dates) maps to all; unresolvable dates are dropped. A phase is persisted only when `apply_start_time` is known **and** ≥1 covered event resolves (else dropped; it may resolve on a later run once concert discovery has stored the events).
- **Alternative considered**: extend the concert searcher / broaden grounding to play-guide pages. Rejected — raises hallucination risk on the fields that drive notifications and couples two concerns.

### Decision 3: Flat optional fields; nullable timestamps mean "TBD"
Method-dependent fields are flat optional (no `oneof`). `method`/`channel` are optional enums where `UNSPECIFIED` = not yet determined. `apply_start_time` is **required** (a phase with no known start is dropped — see Decision 2); the other timestamps are nullable. Because each phase is reified as its own row, **the row's existence signals "this phase is happening"** and a null timestamp unambiguously means "date not yet announced" — no dedicated TBD flag is needed (unlike Ticketmaster's inline `startTBD`).

### Decision 4: Orthogonal dimensions instead of one conflated tier enum
`method` (LOTTERY/FIRST_COME), `channel` (FAN_CLUB/OFFICIAL/PLAYGUIDE/CREDIT_CARD/MOBILE_CARRIER/GENERAL), `sequence` (int: 0=earliest, 1=first round, 2=second…), and `provider_name` (free string, e.g. "イープラス"). Rounds/legs are ordinals (`sequence`), so additional rounds or a first/second-half split need no schema change; the enum only captures the slowly-changing "who/where" gate.

### Decision 5: Surrogate phase id + collision-free logical identity for idempotent upsert
Each phase has a surrogate `id` (UUID PK) used as its stable handle. The discovery job re-runs over the same series, so re-extraction must converge to the same row without collapsing two distinct phases into one. Keying solely on `(series_id, channel, sequence)` is unsafe: both `channel` and `sequence` may take default values (`UNSPECIFIED`, `0`) for phases the searcher cannot classify, so two distinct phases would collide and silently overwrite each other. Instead the `stable_key` is `(series_id, channel, sequence, anchor_event_id)`, where `anchor_event_id` is the earliest (by date) event the phase covers. `anchor_event_id` is the key distinguisher between sibling phases that share `channel`/`sequence` — most importantly per-leg phases (first-half vs. second-half), which differ precisely in which events they cover. It is chosen over `apply_start_time` because **`event_id` is immutable** whereas `apply_start_time` is revised as announcements firm up; a volatile field in the key re-keys the phase into a duplicate on the next run. The `stable_key` is frozen at first insert and never recomputed; mutable fields (timestamps / `provider_name` / `url` / covered-event set beyond the anchor) are last-write-wins but SHALL NOT change it. The surrogate `id` is what the reminder sent-log references.

### Decision 6: Two notification paths — event-driven announcement, time-based reminders
These react to different triggers and are built differently:

**6a — Announcement (event-driven).** When `sales-phase-discovery` upserts a **new** phase, it publishes a `SALES_PHASE.discovered` event; a consumer pushes "a new sales phase was announced" to the relevant followers. This reuses the existing discovery→event→`NotifyNewConcerts`-style pipeline exactly; no scan involved.

**6b — Reminders (time-based scan).** Milestone reminders fire at future times (application open, 24h before close, 1h before close, lottery-result day) that emit no event when they arrive, so a `sales-reminders` CronJob (~15-minute cadence, finer than the tightest 1h window) scans `sales_phases` for milestones that became due since the last run and not yet sent, then pushes. A periodic scan (not pre-scheduled messages) is chosen because sales schedules are **volatile** — the searcher revises timestamps as announcements firm up — so each scan reads current truth and follows changes automatically, is restart-safe, and reuses the `concert-discovery` pattern with no new infra.
- **Alternative considered (6b)**: pre-scheduled delivery at exactly T (e.g. Cloud Tasks `scheduleTime`). Rejected — no such primitive exists in the current broker, and volatile schedules would require constant cancel/re-enqueue on every phase update.

**Shared audience + idempotency.** Both paths resolve recipients via each phase's **covered events** (the `event_sales_phases` join) → performers → followers (hype-filtered, reusing `NotifyNewConcerts`), and send via the existing `webpush.Sender`. A first-half phase therefore notifies only followers relevant to first-half dates. Reminder once-only delivery is guaranteed by a `sales_phase_reminders` sent-log keyed by `(user_id, sales_phase_id, stage)` — using the phase's surrogate `id` — so one phase's reminders never conflate with a sibling phase of the same series that differs only by `channel`.

**6c — Quiet hours.** Reminders must not wake users at night. The existing `users.time_zone` column (already present, commented "IANA time zone identifier for scheduling notifications") gives each user's timezone; when unset, fall back to `Asia/Tokyo`. A reminder due within 22:00–08:00 local is shifted: non-deadline stages defer to 08:00; deadline-relative stages defer to 08:00 only if still before `apply_end_time`, otherwise are brought forward to the prior 22:00 (never woken, never sent past the deadline). Only milestones occurring after a phase becomes known fire (no retroactive firing of already-past stages at first discovery).

**Notification content.** Both announcement and reminders reuse the existing `NotificationPayload` (`title`/`body`/`url`/`tag`), built **per recipient** so times render in the recipient's `time_zone` and copy is selected by `preferred_language` (default `en`). `title`/`body` name the artist, tour, and channel (generic ticket label when `channel`=UNSPECIFIED) and state the stage's relevant time; `url` deep-links to `phase.url` else the concert detail; `tag` is unique per `(sales_phase_id, stage)`.

### Decision 7: Freeze email-import; disable its entry point only
Keep backend RPCs/parsing/storage and proto unchanged; make the frontend `/import/ticket-email` entry unavailable and remove the dead `share_target` from the manifest. `SalesPhase` stays forward-compatible so a future email revival can upsert into it.

## Risks / Trade-offs

- **Gemini fabricates sales dates or coverage** → wrong reminders, or a phase attached to the wrong dates. Mitigation: verbatim Step-1 extraction with retained `source_url`; JSON-coerce only for normalization; map covered dates only to **known** `event_id`s and drop unresolvable ones; persist a phase only when actionable.
- **Dependency on tour bundling** → if the concurrent `auto-discovery-series-grouping` session slips, a tour is still many per-(venue, date) Series, so a phase degenerates to covering one event and per-leg phases cannot form. Mitigation: coordinate sequencing with that session; the model is correct the moment tour-level Series lands, with no `SalesPhase` migration.
- **Reminder noise to uninterested followers** (audience is hype-filtered followers of covered-event performers, not only ticket-seekers, because `TicketJourney` linkage is deferred) → Mitigation: hype-level filtering as today; narrow by `TicketJourney` later.
- **Lost funnel stage ③** (no win/loss import while email is frozen) → Accepted; recovered when email ingestion is revived.
- **Scan cadence vs. precision** (15-min scans → reminders up to ~15 min late) → Acceptable for ticket timings; cadence tunable.

## Migration Plan

- Additive only: new `sales_phases`, `event_sales_phases` (join), and `sales_phase_reminders` tables; new `sales_phase.proto`. No change to `ticket_emails` or `ticket_email.proto`.
- **Coordinate with the `auto-discovery-series-grouping` session**: this design assumes tour-level `Series`; align on `Series` semantics before backend persistence lands.
- **Archive ordering**: this change's `ticket-email-import` delta is `MODIFIED`, which presumes a canonical `ticket-email-import` spec. That capability is still an in-flight change with no archived spec, so `ticket-email-import` MUST be archived before this change, else the `MODIFIED` baseline is missing and the disable delta fails to apply (or is silently dropped). If that ordering cannot be guaranteed, re-express the disable as `ADDED` requirements.
- Proto release follows the standard cross-repo flow (specification PR → merge → Release → BSR gen → backend pin bump → type swap).
- Deploy the two new CronJobs after the backend image carries the job entrypoints.
- Rollback: disable/remove the CronJobs; the additive tables and proto are inert if unused.

## Open Questions

- Trigger cadence for `sales-phase-discovery` (daily vs. follow-triggered re-scan when a new series appears) — defaulting to daily.
- Robustness of loose-leg coverage resolution (e.g. "東名阪公演") in edge cases; mitigated by candidate injection + drop-unresolvable, but accuracy on vague announcements is a quality risk to monitor.
- Whether to surface `SalesPhase` on the concert-detail response now (compose applicable phases on `Concert`) or defer to the F dashboard phase.
- Whether the frontend already captures `users.time_zone` (the column exists); if not, capturing the browser IANA timezone at signup/login is a small follow-up (quiet hours falls back to JST until then).
