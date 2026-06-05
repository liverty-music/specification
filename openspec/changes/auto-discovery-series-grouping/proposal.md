## Why

The `add-series-hierarchy` change shipped a 1-`Series`-per-`Event` SINGLE fallback and explicitly deferred real tour grouping to this change. Today `concert_creation_uc.go` derives `seriesID = UUIDv5(venueID|local_date)` for every discovered date, so a multi-stop tour fragments into many single-row SINGLE series. This blocks every series-level feature (sales timeline, tour-level UI, merch) because no single object represents "the tour". Gemini Step 1 already groups dates under `<tour>` blocks, but `parseStep1Envelope` flattens that grouping away.

Exploring the fix surfaced a deeper structural issue. Series identity is currently load-bearing **inside** the events natural key `(series_id, local_event_date, venue_id)`: `series_id` is forced to be a deterministic `UUIDv5` purely so that re-discovery collides on UPSERT. This couples two concerns that should be independent — *how events deduplicate* and *how events group into a series* — and it forced `series` to be the only table whose UUID CHECK is relaxed to allow v5. The same coupling leaves real defects: the natural key omits `start_at`, so two shows at the same venue on the same date (matinee/evening — 昼夜2公演) collapse into one row at the database layer even though the discovery pipeline already keeps them distinct.

This change separates the two concerns: **events deduplicate on their physical identity, and a series is just a grouping parent whose identity is derived from its member events.**

## What Changes

- **Preserve Gemini's tour grouping.** Stop flattening the `<tour>`→events relationship in `parseStep1Envelope`; carry a tour/standalone marker and an intra-run tour-group handle through `EventDraft` → `ScrapedConcert`.
- **Re-base the events natural key on physical identity.** `(series_id, local_event_date, venue_id)` → `(venue_id, local_event_date, start_at)` with `UNIQUE … NULLS NOT DISTINCT`. `series_id` leaves the key; `start_at` joins it so 昼夜2公演 persist as distinct rows. **This requires a DB migration.**
- **Resolve event identity in the application** (find-or-create), so a later-announced `start_at` fills the existing NULL-start row instead of inserting a duplicate, and a genuinely new start time at the same venue/date becomes a new row.
- **Derive series identity from member events (FK adoption).** When writing a tour group, reuse the `series_id` that the group's events already belong to; only mint a fresh `UUIDv7` series when none exist. Series gets **no content-derived key and no database uniqueness**; its v5 carve-out is removed and `series.id` becomes a normal `UUIDv7`. `SeriesType` is assigned from the Gemini block (TOUR for `<tour>`, SINGLE for `<standalone>`).
- **Disambiguate multi-hall venues via `venue_id`.** Distinct halls already resolve to distinct Google Places IDs (verified empirically), so the physical key needs no raw venue text.

## Capabilities

### New Capabilities
- `auto-discovery-series-grouping`: discovery-time grouping — one `Series` per Gemini `<tour>` group via event-derived identity, a physical event natural key with application-layer resolution, SeriesType assignment, and multi-hall venue disambiguation. This replaces the 1:1 SINGLE fallback deferred by `add-series-hierarchy`.

### Modified Capabilities
- `gemini-grounded-extract-and-coerce`: `parseStep1Envelope` SHALL no longer discard the tour grouping; each `EventDraft` SHALL carry its block origin (tour/standalone) and, for tours, an intra-run group handle.
- `event-management`: the events natural key SHALL be `(venue_id, local_event_date, start_at)` (was `(series_id, local_event_date, venue_id)`); series identity SHALL be established by application-layer adoption from member events rather than by a database-level key.

## Impact

- **specification**: No proto change — `start_at` / `local_date` / `venue` and the `Series` / `SeriesType` enum already exist. Delta specs only, for the three capabilities above.
- **backend**:
  - `internal/infrastructure/gcp/gemini/searcher.go` — `parseStep1Envelope`, `EventDraft` gains block-origin + intra-run tour-group handle.
  - `internal/entity/concert.go` — `ScrapedConcert` carries the same; SeriesType selection.
  - `internal/usecase/concert_creation_uc.go` — application-layer event find-or-create (NULL-start fill vs new session) + series FK adoption (reuse existing `series_id`, else mint `UUIDv7`).
  - `internal/infrastructure/database/rdb/concert_repo.go` — natural-key UPSERT and the `event_performers` JOIN re-keyed to `(venue_id, local_event_date, start_at)`.
  - schema + **Atlas migration** — drop the old constraint, deduplicate existing rows, add `UNIQUE (venue_id, local_event_date, start_at) NULLS NOT DISTINCT`, relax `series.id` CHECK to pure `UUIDv7`.
  - unit + integration tests.
- **No cross-repo BSR flow** (no proto change) — backend-only PR.
- **Eliminated risk** (previously "accepted, logged"): divergent-title co-headline tours and tour-stop/standalone collisions no longer duplicate — events collapse on physical identity and the series is adopted, independent of title/URL.
