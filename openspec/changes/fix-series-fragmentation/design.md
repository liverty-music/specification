## Context

The `auto-discovery-series-grouping` capability already specifies that a `<tour>` block persists as one TOUR series (identity adopted from member events; events dedup on the physical natural key `uq_events_natural_key(venue_id, local_event_date, start_at)` which is already in the schema). But the persistence code never implemented the grouping: `concert_creation_uc.CreateFromDiscovered` loops per concert and `buildAndInsertConcerts` adopts a series only from an existing event at THIS `(venue, date)`; a new tour's sibling events have distinct natural keys, so each mints its own series. `TourGroup`/`IsTour` are carried on `ScrapedConcert` but never consulted. The admin approval path shares `buildAndInsertConcerts`, and `staged_concerts` carries no grouping, so approvals fragment and mis-type SINGLE. See proposal.md — Why. This is therefore a spec-conformance fix, taken as a zero-based model redesign for maintainability.

## Goals / Non-Goals

**Goals:**
- Make per-event fragmentation structurally impossible (not just patched) by modeling discovery as series-grouped.
- Fix both the discovery auto-publish AND the admin approval paths with one consistent mechanism.
- Unify the `TourGroup`/`IsTour` naming around `Series`/`SeriesType`.
- Clean up existing fragmented production data.

**Non-Goals:**
- Renaming the broader `event` vs `concert` duplication (`events`/`concerts`/`ScrapedConcert`/`staged_concerts`) — possible follow-up.
- Changing the events natural key or the series-identity model (both already correct in schema + spec).
- Sales-phase prompt/quality work (separate) and merch deprecation (separate; drops `series.merch_url`).
- FESTIVAL series: concert discovery deliberately excludes multi-artist festivals, so discovery emits only TOUR/SINGLE. The `FESTIVAL` `SeriesType` stays defined (schema/entity/spec) but unproduced by this path; festival ingestion is a separate concern and must not be shoe-horned into TOUR here.

## Decisions

### Model discovery as series-grouped (not flat events + flags)
Replace the flat `ConcertDiscoveredData{ Concerts: []ScrapedConcert{…, IsTour, TourGroup} }` with a grouped shape: `ConcertDiscoveredData{ Series: []DiscoveredSeries{ Title, Type, SourceURL, Events: []DiscoveredEvent{ venue, date, start, open } } }`. The Gemini `<tour>`/`<standalone>` blocks map to `SeriesType` TOUR/SINGLE at parse time. This makes grouping the structure of the data, moves `source_url` to the series level (where the DB already keeps it), and deletes the `IsTour` bool + `TourGroup` int entirely. Alternative considered: keep the flat model and add a within-batch `map[TourGroup]seriesID` — rejected: it patches discovery only, leaves the naming split, and does not fix the approval path; grouping stays an easily-re-broken afterthought.

### Resolve series_id ONCE per group, at discovery time
For each `DiscoveredSeries`, resolve the series before splitting events into auto-publish vs stage: query existing events across ALL the group's `(venue, date)` pairs; if any carries a `series_id`, adopt it; otherwise mint one fresh `UUIDv7` with the group's `SeriesType`, and **upsert the `series` row now** (title / type / source_url). Because the series row exists as soon as its id is resolved — before any event, published or staged — both `events.series_id` and `staged_concerts.series_id` are plain foreign keys: there is no soft reference, no lazy "materialize on first approval", and no concurrency guard. Every publishable event inserts under that `series_id`; every staged event carries it forward, so approval just inserts the event and never re-derives identity. (This generalizes the old "mint only when the first member event exists" rule: the series row is created when its id is first resolved, which is the same transaction for an all-auto-publish group and slightly earlier for a group that stages some events.)

Grouping is per-`DiscoveredSeries` (one Gemini `<tour>` block from one artist's run) — there is NO title-based grouping key at discovery time. Cross-artist co-headline convergence is not done by matching titles: it happens at the event level via the natural-key dedup — when a second artist's run discovers the same physical show (same `venue_id, local_event_date, start_at`), that event already exists and already carries a `series_id`, which the group adopts. Divergent titles therefore still converge to one series.

Deploy ordering: the data migration (§Migration — an Atlas migration that runs ahead of the backend Deployment via the operator sync-wave) consolidates existing fragments FIRST, so once deployed the group query returns at most one existing series. The MULTIPLE-existing-series branch is a defensive fallback only (adopt the earliest `UUIDv7`); it must not occur in normal operation after the migration has run.

### Series-aware staging; approval stays per-event
Because the `series` row is created when the group's `series_id` is resolved (above), `staged_concerts.series_id` is a **real foreign key** and staging carries only that `series_id` — `type`, `title`, and `source_url` live on the referenced series row, not duplicated on staged (and `staged_concerts` never had `is_tour`/`tour_group` columns to begin with). Only two things get staged — unresolved venue and same-slot conflict — both per event, so approval granularity stays per-event: the operator approves an individual staged event, which simply inserts its event under the existing `series_id`. No materialize/adopt branching, no idempotency guard.

Venue resolution is ordered within a group: resolve every event's venue first (Places API, cached per batch), then resolve+create the group's series once, then decide per event whether to auto-publish or stage. A partially-resolvable group is fine — resolved events publish, unresolved (and conflicting) ones stage, all under the same `series_id`.

A series row may transiently have zero events (all its events staged, or a group later fully rejected). This is harmless and is swept by a lightweight cleanup: delete any series that has no events AND no pending staged rows.

### Publish once per series; reuse the grouping that already exists
Emit one `CONCERT.created` per discovered series carrying all its newly-inserted event ids (`ConcertCreatedData.ConcertIDs` is already a list), instead of one message per event. A multi-date tour then wakes the notification consumer ONCE (one follower/proximity/hype pass) rather than N times for the same artist+series — the per-event publish is redundant work the series-grouped model lets us drop. The redesign also preserves the tour grouping that ALREADY exists in the Step 1 XML (`<tour>`/`<standalone>` blocks → `EventDraft.TourGroup`) end-to-end rather than re-deriving it downstream, and factors the group series-resolution (adopt-across-the-group's-venues/dates, else mint) into ONE helper reused by both the discovery persistence and any approval-time path — so the two paths cannot drift.

### Migration: in-place consolidation (DECIDED — production-measured 2026-08-25)
Consolidate, do not delete. The production measurement showed consolidation is clean and low-cost: 382 fragmented series collapse to ~58 groups (367 series across 43 multi-series groups; worst 28) and only **6** events carry user data (`ticket_journeys`; `ticket_emails` is empty), so the delete fallback would lose real user data for no benefit and force a full re-discovery + sales-phase-rediscovery rebuild.

The migration groups by `(source_url, type)` where a `source_url` exists, falling back to `(normalized title, type)` only when it is empty — and NOT by artist. Prefer `source_url` because it is the tour's stable feature/announcement page: it does NOT drift when the promoted title is re-branded, re-localized, or has dates appended, whereas `(title, type)` mis-splits one real tour on exactly that drift. A co-headline tour discovered under two artists must consolidate to ONE series (artists stay linked via `event_performers`), so artist is not a grouping dimension; the `(artist, title, type)` = 58 figure over-counts multi-artist groups. For each group it mints one canonical TOUR series (keep the earliest `UUIDv7`) and re-points `events.series_id` + `sales_phases.series_id` to it. It then dedups `sales_phases` on the FULL business tuple `(series_id, apply_start_at, method, channel, provider_name)` — NOT just `(series_id, apply_start_at)` — keeping the earliest `discovered_at`, so two genuinely-distinct phases that share a start time (e.g. an FC lottery and a general on-sale) are preserved (measurement: 208 rows → 70 distinct on that tuple). It sets `type = TOUR` for consolidated multi-event groups and deletes the emptied series. Events — and their `ticket_journeys` — are preserved. The delete-and-rebuild fallback is rejected. Residual risk: rows lacking a `source_url` fall back to `(title, type)` and can still title-drift-split; the measured 367/382 exact-title consolidation shows this is a small tail — genuine single-event SINGLE series (~15 groups) are correctly left alone.

## Risks / Trade-offs

- **Blast radius**: the model reshape touches the searcher output, entity model, wire payload, publisher, consumer, both persistence paths, `staged_concerts` schema, and tests. Larger than a within-batch patch, but bought once for a structurally-correct, maintainable model.
- **Migration data-loss risk**: consolidation preserves events + user data; the dedup MUST key on the full phase tuple (method/channel/provider), not just `(series_id, apply_start_at)`, or it drops distinct same-start phases. Residual: the `(title, type)` fallback (rows with no `source_url`) can mis-split on title drift (small tail per measurement).
- **Zero-event series**: eager series-row creation allows a series to transiently exist with no events (all its events staged, or a group later fully rejected). Harmless, and swept by a lightweight cleanup — delete any series with no events AND no pending staged rows. Cheaper than the soft-FK + materialize-on-approval + concurrency-guard machinery it replaces.
- **Process gap**: the `auto-discovery-series-grouping` spec was archived with the schema in place but the use-case grouping never shipped — worth a lightweight guard (e.g., an integration test asserting a multi-date tour yields one series) so it cannot silently regress again.

## Open Questions

- **Migration approach** — RESOLVED 2026-08-25 by production measurement: in-place consolidation (see Decisions → Migration). 382 series → 58 `(artist, title, type)` groups; 6 events with user data; `sales_phases` 208 → 70.
- **Include `event`/`concert` naming cleanup in this change, or defer?** Default: defer (keeps blast radius bounded). Still open.
