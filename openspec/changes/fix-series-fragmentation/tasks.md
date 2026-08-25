# Tasks

## 1. Measurement — resolve the migration approach (read-only prod SELECT) — DONE 2026-08-25

- [x] 1.1 Measured series-count-per-`(artist, title, type)` in prod: 382 series → 58 groups (43 multi-series groups cover 367 series; worst 28) — exact-title consolidation is clean
- [x] 1.2 Counted user-data events: 6 `ticket_journeys` events, 0 `ticket_emails`
- [x] 1.3 DECIDED: in-place consolidation (folded into design.md → Migration; concretized in section 5)

## 2. Series-grouped discovery model

- [ ] 2.1 Define `DiscoveredSeries` / `DiscoveredEvent` entities; reshape `ConcertDiscoveredData` to carry `Series[]`; remove `IsTour` / `TourGroup`
- [ ] 2.2 Emit series-grouped output from the Gemini searcher (map `<tour>` / `<standalone>` → `SeriesType`; `source_url` at the series level)
- [ ] 2.3 Update the publisher (`concert_uc`) to publish the grouped payload
- [ ] 2.4 Update the discovery consumer (`concert_consumer.go`) to deserialize the grouped payload, and update the searcher test that asserts the old `TourGroup` shape (`searcher_test.go` `TestParseStep1Envelope_TourGrouping`) to the series-grouped shape

## 3. Per-series persistence (discovery)

- [ ] 3.1 Extract ONE shared helper `resolveSeriesForGroup(ctx, venueIDs, dates, seriesType) (series_id, existed bool)` — adopt from the group's existing events across all venue/dates, else mint a `UUIDv7`; reuse it in discovery and any approval-time path so the two cannot drift
- [ ] 3.2 Resolve all group venues FIRST (Places API, per-batch cache), THEN call the helper ONCE per group and **upsert the `series` row now** (title / type / source_url) — so the series row exists before any event references it; insert every publishable event under that `series_id`
- [ ] 3.3 Carry ONLY `series_id` onto staged events (both the unresolved-venue and same-slot-conflict staging paths); `type` / `title` / `source_url` live on the already-created series row, not duplicated on staged
- [ ] 3.4 Preserve the Step 1 XML tour grouping (`<tour>`/`<standalone>` → `EventDraft.TourGroup`) end-to-end into `DiscoveredSeries`; do not re-derive grouping downstream

## 4. Series-aware staging & approval

- [ ] 4.1 Add `series_id` to `staged_concerts` as a **real foreign key** (schema + entity, Atlas migration) — the series row always exists by staging time (§3.2); do NOT add `series_type` / `source_url` / `title` (derivable from the series row), and it has no `is_tour`/`tour_group` columns to remove
- [ ] 4.2 Approval simply inserts the event under the carried `series_id` — no materialize/adopt branching and no idempotency guard (the series row already exists); keep per-event approval granularity
- [ ] 4.3 Publish ONE `CONCERT.created` per discovered series with all newly-inserted event ids (`ConcertIDs` is already a list), from BOTH the auto-publish and approval paths — not one message per event — so a multi-date tour wakes the notification consumer once
- [ ] 4.4 Add a lightweight cleanup that deletes any series with no events AND no pending staged rows (sweeps the transient/rejected zero-event series that eager creation allows)

## 5. Data migration — in-place consolidation (Atlas)

- [ ] 5.1 Group fragmented series by `(source_url, type)` where `source_url` is present (stable tour page — survives title re-branding), falling back to `(normalized title, type)` only when empty; NOT by artist (a co-headline tour spans artists but is one series); mint one canonical TOUR series per group (keep the earliest `UUIDv7`); re-point `events.series_id` and `sales_phases.series_id` to it
- [ ] 5.2 Dedup `sales_phases` on the FULL phase tuple `(series_id, apply_start_at, method, channel, provider_name)` keeping the earliest `discovered_at` (208 → ~70 rows) — do NOT dedup on `(series_id, apply_start_at)` alone or distinct same-start phases (FC lottery vs general on-sale) are lost; set `type = TOUR` for consolidated multi-event groups; delete the emptied fragmented series
- [ ] 5.3 Sequence the migration to run AHEAD of the new per-series backend Deployment (Atlas operator sync-wave, so consolidated data exists before the new code deploys); make it re-runnable and snapshot `(series/events/sales_phases.series_id)` for rollback before mutating
- [ ] 5.4 Verify post-migration with SQL: 1-event-series count collapses (~382 → ~58), `sales_phases` ~208 → ~70 rows, consolidated multi-event groups typed TOUR, and `count(distinct event_id)` in `ticket_journeys` unchanged (= 6, none lost)

## 6. Tests & guardrails

- [ ] 6.1 Unit tests: a multi-date tour yields ONE series (discovery); a staged tour event joins the tour series on approval; `SeriesType` preserved through approval
- [ ] 6.2 Add a regression guard in `concert_creation_uc_test.go` asserting a multi-date discovered tour persists as exactly ONE `series_id` typed TOUR — the invariant the archived spec required but was never enforced
- [ ] 6.3 `make check` (lint + tests) green
