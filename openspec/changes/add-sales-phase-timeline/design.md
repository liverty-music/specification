## Context

New-concert discovery and follower push notifications already exist (`auto-concert-discovery` + Web Push). What is missing is any objective record of the **ticket sales timeline**: application open/close, lottery-result announcement, and payment deadline. `TicketJourney` only holds a fan's self-reported status; it carries no schedule.

Two findings from codebase exploration shape this design:

1. The existing Gemini concert searcher (`internal/infrastructure/gcp/gemini/searcher.go`) grounds only on the artist's **official site** plus brand-domain Google Search. Sales schedules live on play-guide platforms (e+, ぴあ, ローチケ) and are essentially absent from that grounding. So sales-phase extraction needs a **separate, purpose-built searcher**, not an extension of the concert searcher.
2. There is **no delayed/scheduled-message capability** (NATS JetStream fires immediately). The established pattern for time-based work is a periodic CronJob that scans and publishes (`concert-discovery`). Multi-stage reminders follow that pattern.

A third constraint is product-level: the `ticket-email-import` feature's ingestion entry point (PWA Share Target from the Android Gmail app) no longer works because Gmail removed its share action. Email is therefore frozen for now, leaving the sales-phase searcher as the sole writer of sales-schedule data.

## Goals / Non-Goals

**Goals:**
- Model the ticket sales timeline as a first-class, Series-scoped `SalesPhase` entity.
- Populate it automatically via a dedicated Gemini searcher that takes artist + series and extracts that series' sales phases, with discipline to avoid hallucinated dates.
- Fire multi-stage push reminders (application open, 24h before close, 1h before close, lottery-result day) to performers' followers, reusing existing Web Push infrastructure.
- Cleanly disable the unusable email-import entry point without deleting its code.

**Non-Goals:**
- Importing lottery win/loss results (private inbox data) — funnel stage ③. Deferred to an email-revival phase.
- `TicketJourney`↔`SalesPhase` linkage (`phase_id`).
- Per-user first-come (conbini) payment deadlines (pattern B).
- The F "Next Action" dashboard and C merch features.
- Refactoring frozen `TicketEmail` storage onto `SalesPhase`.
- Firing payment-deadline reminders. `payment_deadline_time` is captured on `SalesPhase` (objectively knowable for pattern-A unified deadlines) as a **forward-compatible field** for a future win/loss-gated payment reminder (funnel stage ③). It is intentionally NOT a reminder stage in this change, because a blanket "payment due" reminder to all followers — including non-winners — would be wrong; a correct payment reminder requires the per-user win/loss signal, which is deferred with email.

## Decisions

### Decision 1: `SalesPhase` is Series-scoped (`series_id` FK), not Event-scoped
Sales phases (FC presale, general sale) are announced once per tour/series and apply to all its dates; the application window, lottery-result time, and payment deadline are shared across the series. Modeling per-Event would duplicate one phase across every tour date.
- **Prerequisite — depends on `auto-discovery-series-grouping`.** Today `Series` is derived per-`(venue, date)` (SINGLE fallback), so a tour is scattered across many single-row series; Series-scoping a `SalesPhase` would then still fragment per date. This design assumes `auto-discovery-series-grouping` has made a `Series` represent a whole tour. That change is the prerequisite and SHOULD land first.
- **Alternative considered**: Event-scoped (`event_id` FK). Rejected — duplicates phases across tour dates and mismatches the series-scoped searcher input. Standalones are series-of-one, so Series scope covers them too.
- The fan's per-date result remains Event-scoped on `TicketJourney` (unchanged), giving a clean split: objective schedule at Series grain, subjective result at Event grain.

### Decision 2: Dedicated sales-phase searcher, separate from concert search
Concert grounding (official site) does not contain sales schedules. The new searcher takes `artist name + series title`, loops one Gemini call per series, and follows the existing two-step discipline: Step 1 grounded **verbatim** extraction (keep `source_url`), Step 2 JSON coercion of dates. A phase is only persisted when actionable data is present (≥1 timestamp, or method + URL), preventing empty-phase noise.
- **Alternative considered**: Extend the concert searcher to also pull sales info, or broaden its grounding to play-guide pages. Rejected — increases hallucination risk on the most consequential fields (dates that drive notifications) and couples two distinct concerns.

### Decision 3: Flat optional fields; nullable timestamps mean "TBD"
Method-dependent fields are flat optional (no `oneof`). `method`/`channel` are optional enums where `UNSPECIFIED` = not yet determined. All timestamps are nullable. Because each phase is reified as its own row, **the row's existence signals "this phase is happening"** and a null timestamp unambiguously means "date not yet announced" — so no dedicated TBD flag is needed (unlike Ticketmaster's inline `startTBD`).

### Decision 4: Orthogonal dimensions instead of one conflated tier enum
`method` (LOTTERY/FIRST_COME), `channel` (FAN_CLUB/OFFICIAL/PLAYGUIDE/CREDIT_CARD/MOBILE_CARRIER/GENERAL), `sequence` (int: 0=earliest, 1=first round, 2=second…), and `provider_name` (free string, e.g. "イープラス"). Rounds are an ordinal (`sequence`), so third/fourth rounds need no schema change; the enum only captures the slowly-changing "who/where" gate.

### Decision 5: Idempotent upsert key `(series_id, channel, sequence)`
The daily discovery job re-runs over the same series; the upsert key lets re-extraction converge to one row per phase, with timestamps/`provider_name`/`url` last-write-wins. (With email frozen, there is a single writer; the key still guarantees re-run idempotency and keeps the model ready for a second writer later.)

### Decision 6: Reminders via periodic CronJob scan + sent-log
A `sales-reminders` CronJob (~15-minute cadence, finer than the tightest 1h window) scans `sales_phases` for due milestones, resolves series → performers → followers (hype-filtered, reusing `NotifyNewConcerts`), publishes a reminder event, and a consumer sends Web Push via the existing `webpush.Sender`. A `sales_phase_reminders` sent-log with a unique key `(user_id, series_id, sequence, stage)` guarantees once-only delivery despite overlapping scans.
- **Alternative considered**: Delayed/scheduled messages. Rejected — no such broker capability exists; would add infrastructure for no benefit over the proven scan pattern.

### Decision 7: Freeze email-import; disable its entry point only
Keep backend RPCs/parsing/storage and proto unchanged; make the frontend `/import/ticket-email` entry unavailable and remove the dead `share_target` from the manifest. `SalesPhase` stays forward-compatible so a future email revival (manual paste or Gmail API) can upsert into it.

## Risks / Trade-offs

- **Gemini fabricates sales dates** → Reminders would fire on wrong times. Mitigation: verbatim Step-1 extraction with retained `source_url`, JSON-coerce only for normalization, and persist a phase only when actionable fields are present.
- **Reminder noise to uninterested followers** (audience is all hype-filtered followers, not only ticket-seekers, because `TicketJourney` linkage is deferred) → Mitigation: hype-level filtering as today; narrow by `TicketJourney` in a later phase.
- **Lost funnel stage ③** (no win/loss import while email is frozen) → Accepted; recovered when email ingestion is revived.
- **Scan cadence vs. precision** (15-min scans mean reminders can be up to ~15 min late) → Acceptable for ticket timings; cadence tunable.
- **Series granularity edge cases** (a single date with its own extra sale) → Accepted for MVP; per-date override is a future extension.

## Migration Plan

- Additive only: new `sales_phases` and `sales_phase_reminders` tables; new `sales_phase.proto`. No change to `ticket_emails` or `ticket_email.proto`.
- **Archive ordering**: this change MODIFIES the `ticket-email-import` capability, so it MUST be archived after the in-flight `ticket-email-import` change is archived (otherwise the MODIFIED baseline requirements are absent from `openspec/specs/`). Implementation/merge order is independent; this constraint applies at OpenSpec archive time.
- Proto release follows the standard cross-repo flow (specification PR → merge → Release → BSR gen → backend pin bump → type swap).
- Deploy the two new CronJobs after the backend image carries the job entrypoints.
- Rollback: disable/remove the CronJobs; the additive tables and proto are inert if unused.

## Open Questions

- Trigger cadence for `sales-phase-discovery` (daily vs. follow-triggered re-scan when a new series appears).
- Whether to surface `SalesPhase` on the concert-detail response now (compose `repeated SalesPhase` on `Concert`) or defer to the F dashboard phase.
- Exact reminder-notification copy/payload shape.
