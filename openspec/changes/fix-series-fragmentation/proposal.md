## Why

Production discovery data is badly fragmented: **381 of 382 `series` rows have exactly one event**, and 74% of `(artist, title)` combinations map to more than one series (worst case 28 series for a single 24-date tour). Every series-level attribute — `sales_phases`, `source_url`, and `merch_url` — is therefore duplicated once per tour date. The `auto-discovery-series-grouping` capability already SPECIFIES the correct behavior (a `<tour>` block persists as one TOUR series) and the DB schema already has the right constraints (`uq_events_natural_key`), but the persistence code never implemented it: `CreateFromDiscovered` processes discovered concerts one-by-one and mints a fresh series per event, ignoring the `TourGroup` grouping. The admin approval path is worse — `staged_concerts` carries no grouping at all, so every approved concert fragments AND is mis-typed SINGLE.

This change conforms the implementation to the spec via a **zero-based redesign of the discovered-concert model** (prioritizing maintainability and extensibility), unifies the inconsistent `TourGroup` / `IsTour` naming around the `Series` concept, and cleans up the fragmented production data.

## What Changes

- **Discovered-concert model becomes Series-grouped** — the discovery payload carries `DiscoveredSeries { title, type, source_url, events[] }` instead of a flat `[]ScrapedConcert` with per-event `IsTour` / `TourGroup`. Grouping becomes structural, so per-event fragmentation is impossible by construction; `source_url` moves to where it belongs (series-level).
- **Persistence is per-series** — the `series_id` is resolved ONCE per discovered series group (adopt the `series_id` carried by any already-persisted member event across the group's venue/dates, else mint one fresh `UUIDv7` with `type` from the source block) via a single shared helper reused by discovery and approval. The `series` row is created at that point, so every publishable event in the group is inserted under an already-existing shared `series_id`.
- **Approval preserves grouping** — because the series row is created at discovery, `staged_concerts` needs only a real-FK `series_id` (no `series_type` / `source_url` / `title` duplication; it carried no tour-grouping fields before). Per-event approval simply inserts the event under the existing series — no materialize/adopt branching and no concurrency guard. Approval granularity stays per-event (only unresolved-venue and same-slot-conflict events are staged). A lightweight cleanup deletes any series left with no events and no pending staged rows.
- **Publish once per series** — one `CONCERT.created` per discovered series carrying all its new event ids (from both the auto-publish and approval paths), instead of one message per event, so a multi-date tour wakes the notification consumer once.
- **Naming unified** — `IsTour` and `TourGroup` are removed; `Series` / `SeriesType` are used consistently from extraction through persistence (the tour grouping already present in the Step 1 XML is preserved end-to-end, not re-derived).
- **Existing fragmented data is cleaned up** — **in-place consolidation** (decided 2026-08-25, production-measured): group fragmented series by `(source_url, type)` where present (the stable tour page, which survives title re-branding), falling back to `(title, type)` only when empty — never by artist (a co-headline tour spans artists but is one series); mint one canonical TOUR series per group, re-point `events.series_id` + `sales_phases.series_id`, dedup `sales_phases` on the full phase tuple `(series_id, apply_start_at, method, channel, provider_name)`, and delete the emptied series — preserving user-owned `ticket_journeys` on events. 382 series → ~58 groups; only 6 events carry user data; the delete-and-rebuild fallback is rejected.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `auto-discovery-series-grouping`: the discovery payload is delivered grouped by series and the persistence path groups a tour's events under one series (conforming to the existing requirements); ADDED — the admin **approval path** SHALL also preserve series grouping and assign `SeriesType` from the discovered series (today it fragments and mis-types SINGLE).

## Impact

- **Code**: `internal/entity/concert.go` + `event_data.go` (Series-grouped discovery model; drop `IsTour`/`TourGroup`), `internal/infrastructure/gcp/gemini/searcher.go` (emit series-grouped output, preserving the Step 1 XML tour grouping), `internal/usecase/concert_uc.go` (publish shape → one `CONCERT.created` per series), `internal/usecase/concert_creation_uc.go` (`buildAndInsertConcerts` → per-series via the shared series-resolution helper; create the series row at resolution), `internal/usecase/concert_admin_uc.go` (approval inserts under the existing carried series; series cleanup), `internal/entity/staged_concert.go` + `staged_concerts` schema (add real-FK `series_id` only; it had no tour-grouping fields to drop), plus affected tests (incl. the searcher test that asserts the old `TourGroup` shape) and the discovery consumer.
- **DB migration**: Atlas migration for the `staged_concerts` shape change and the one-time data consolidation/cleanup.
- **Measurement (done 2026-08-25, read-only prod SELECT)**: 382 series → 58 `(artist, title, type)` groups (367 series across 43 multi-series groups; worst 28); 6 events carry user data (`ticket_journeys`; `ticket_emails` empty); `sales_phases` 208 rows → 70 distinct. → in-place consolidation adopted.
- **Out of scope / possible follow-up**: the separate `event` vs `concert` naming duplication (`events` / `concerts` / `ScrapedConcert` / `staged_concerts`); `series.merch_url` is being dropped by the separate merch-deprecation change. No proto/RPC changes.
