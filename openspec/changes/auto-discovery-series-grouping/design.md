## Context

`add-series-hierarchy` introduced the `Series` parent and the `SeriesType` enum (TOUR/SINGLE/FESTIVAL) but shipped a 1-`Series`-per-`Event` SINGLE fallback, deferring real grouping here. Today `concert_creation_uc.go` derives `seriesID = UUIDv5(venueID|local_date)` and sets `SeriesType = SINGLE` for every discovered date, so a multi-stop tour fragments into many single-row series.

Codebase exploration established the constraints this design works within:

1. **Gemini already groups tours.** Step 1 emits an `<extracted>` envelope with `<tour>` blocks (each `<title>`, `<source_url>`, and multiple `<event>` children) and `<standalone>` blocks (one `<event>`). `parseStep1Envelope` flattens this into a flat `[]EventDraft`, discarding which events belonged to the same tour.

2. **The Gemini prompts segregate by role.** The tour slices extract "%s のツアー" and exclude festivals and standalones; the standalone slice extracts solo / FC / 2–4-act co-headliner 対バン and excludes festivals and tours; 10+-act festivals are out of scope. Co-headliner bills are therefore always `<standalone>`, and either artist's own official site may list the same bill — so the same physical show can be discovered by two artists' runs.

3. **Series identity is currently load-bearing inside the events natural key.** The key is `(series_id, local_event_date, venue_id)`; `series_id` is a deterministic `UUIDv5` only so that re-discovery collides on UPSERT. This couples *event dedup* to *series grouping*, forced `series` to be the only table whose UUID CHECK allows v5, and — because the key omits `start_at` — collapses 昼夜2公演 (matinee/evening at one venue) into a single row at the DB layer even though the discovery pipeline's `(local_date, venue, start_time)` dedup keeps them distinct.

4. **The discovery pipeline already keys on physical identity.** `parseStep2Response` deduplicates on `(local_date, normalized_venue, start_time)` ([searcher.go]), explicitly so Billboard 1st/2nd-stage style same-day shows survive. The DB layer is the only place that loses `start_at`.

5. **Google Places resolves halls to distinct IDs.** Verified live against `places:searchText` (New): 東京国際フォーラム ホール A/B/C, サントリーホール 大ホール/ブルーローズ, Bunkamura オーチャード/コクーン, パシフィコ横浜 国立大ホール/ノース, 東京芸術劇場 コンサートホール/プレイハウス each return a distinct `place_id`. Text drift (whitespace, full/half-width, English/Japanese, abbreviation) is absorbed by Places' fuzzy match to the same ID. Single-hall venues collapse bare-name and main-hall queries to the same building ID.

## Goals / Non-Goals

**Goals:**
- Persist a multi-stop tour as a single `Series` (SeriesType=TOUR) shared by all its events, preserving Gemini's grouping rather than re-deriving it.
- Make event deduplication reflect **physical identity** — same venue, date, and start time is one event; 昼夜2公演 are two.
- Make series identity a **consequence of its events**, not a content-derived key — removing the deterministic-`seriesID` machinery and the `series` v5 carve-out.
- Keep co-headliner cross-artist linkage working (one event row, multiple `event_performers`).

**Non-Goals:**
- Grouping standalones or festivals into multi-event series.
- Reconciling a tour's series across runs when **all** of its previously-seen dates have rotated into the past before new dates appear (the 追加公演 edge — see Risks).
- Recovering which hall a venue reference means when the source omits the hall name (an inherent information gap — see Risks).
- Proto changes.

## Decisions

### Decision 1: Preserve Gemini's tour grouping as an opaque intra-run handle
Carry a tour/standalone marker and a tour-group handle from `parseStep1Envelope` onto `EventDraft`, then onto `ScrapedConcert`. The handle only needs to group events **within a single run** (which `<tour>` block they came from); it is **not** a cross-run series key and does **not** need to be derived from `source_url` or title. Re-deriving the grouping downstream (e.g. clustering on title) would be lossy and redundant.

### Decision 2: Events deduplicate on physical identity `(venue_id, local_event_date, start_at)`
Replace the events natural key `(series_id, local_event_date, venue_id)` with `UNIQUE (venue_id, local_event_date, start_at) NULLS NOT DISTINCT`.
- `series_id` **leaves** the key — event identity is physical, not a function of how we grouped it. This is what lets two artists' independent discoveries (co-headliner, or a divergent-title co-headline tour) collapse onto one row regardless of series.
- `start_at` **joins** the key so 昼夜2公演 persist as distinct rows, matching the pipeline's existing `(date, venue, start)` dedup and an explicit product requirement.
- `NULLS NOT DISTINCT` (PostgreSQL 15+) makes two NULL-start shows at the same venue/date collapse to one row — they are indistinguishable until a start time is published, so collapsing conservatively is correct.
- **Alternative considered — add `listed_venue_name` to the key** (to split same-building different-hall shows): rejected. The raw scraped string drifts across sources and would cause frequent false *splits*; Places already resolves halls to distinct `venue_id`s (Decision 5), so disambiguation belongs in venue identity, not the event key.

### Decision 3: Resolve event identity in the application (find-or-create)
A pure DB constraint cannot both distinguish 昼夜 by `start_at` and merge a later-announced `start_at` into the row first seen with a NULL start (the two have different keys). The use case therefore resolves each scraped event against existing rows before writing:

| Existing row at (venue, date) | Incoming `start_at` | Action |
| --- | --- | --- |
| none | NULL or known | INSERT |
| row with NULL start | known | **UPDATE that row** (fill) — no duplicate |
| row with the same known start | known | UPDATE (idempotent) |
| only rows with *different* known starts | known | INSERT (a new session = 昼夜) |
| any | NULL | match the single / NULL row; else INSERT |

Ambiguous cases default conservatively to **fill** over split. The DB `UNIQUE … NULLS NOT DISTINCT` remains as a backstop against exact-duplicate races. (`start_at`/`open_at` `COALESCE` fill semantics already exist in the UPSERT and are preserved.)

### Decision 4: Series identity is adopted from member events; series has no key
When writing a tour group, look up whether the group's events already exist (by the physical key); if so, reuse their `series_id` for the whole group; otherwise mint a fresh `UUIDv7` series. Within a run, all events of one `<tour>` block share one series (intra-run grouping from Decision 1); across runs, identity is the `series_id` the events already carry.
- `series` gets **no content-derived key and no DB uniqueness**. The v5 carve-out is removed: `series.id` becomes a normal `UUIDv7`, matching every other table.
- This eliminates the deterministic-`seriesID` machinery entirely — `source_url`, generic-URL guards, and title fallback are all gone from series identity. Title/URL drift can no longer split or merge a series.
- **Alternative considered — deterministic `UUIDv5(source_url|title)` for tours**: rejected. It made `series_id` double as a dedup key, required the v5 carve-out, and risked merging unrelated tours that share a generic URL.

### Decision 5: Multi-hall venues are disambiguated by `venue_id`, via Places
Distinct halls resolve to distinct Places IDs (Context §5), so a hall-level `venue_id` carries the disambiguation and the physical key stays clean. Venue resolution already appends `adminArea` to the query and relies on Places' fuzzy match to absorb text drift. The residual is the **information gap** when a source omits the hall name (Risks).

### Decision 6: SeriesType is assigned from the Gemini block, not inferred from event count
A `<tour>` block yields TOUR even if only one date falls in range; a `<standalone>` yields SINGLE even if multi-day. Trusting the source classification avoids fragile count heuristics.

## Risks / Trade-offs

- **追加公演 after full date rotation** → series split. If every previously-seen date of a tour has passed (and been range-filtered out) before newly-announced dates are discovered, the FK-adoption lookup finds no existing events and mints a second series. Low harm — such a late leg is often marketed as a distinct 追加公演; no data loss. *Optional hardening:* carry the tour's true 初日 `(venue, date)` as series metadata captured pre-filter from Gemini's full listing, and adopt on that. Deferred to Open Questions.
- **Concurrency race** → rare double series. Two artists discovering the same tour in concurrent transactions can both find no existing events and each mint a series; the event `UNIQUE` constraint still prevents duplicate event rows, but the events may split across two series. Rare for a low-volume discovery cron; logged. The old deterministic key was implicitly race-safe (independently computed); FK-adoption is not. *Optional hardening:* a transaction advisory lock keyed on a tour anchor to serialize.
- **Multi-hall bare-vs-hall asymmetry** → rare split. If one source names the hall and another omits it, the same show resolves to a hall `venue_id` and a building `venue_id` → two rows. Inherent information gap (cannot recover the hall from a bare reference); narrow because official sites usually name the hall and single-hall venues never split. Logged; monitored via the same "anomalously duplicated series" signal.
- **Gemini misclassifies a one-off as `<tour>`** → a TOUR series with one event. Low harm; SINGLE vs TOUR is cosmetic for a single date.

## Migration Plan

- **DB migration (Atlas), backend repo:**
  1. Deduplicate existing `events` rows that would violate the new constraint (same `venue_id, local_event_date, start_at`, including NULL-start collisions under `NULLS NOT DISTINCT`), repointing `event_performers` to the surviving row.
  2. Drop `uq_events_natural_key` `(series_id, local_event_date, venue_id)`; add `UNIQUE (venue_id, local_event_date, start_at) NULLS NOT DISTINCT`.
  3. Relax `chk_series_id_uuid_v5_or_v7` to `chk_series_id_uuidv7` (pure `UUIDv7`). Existing v5 series rows remain valid data; only new inserts are constrained — so either keep the CHECK permissive for legacy rows or backfill. Pre-launch data volume is small (dev intentionally stopped; prod pre-launch on v1.x), so a clean dedup-then-constrain is feasible.
- **No proto change, no BSR flow.** Backend-only PR.
- **Existing SINGLE series** already persisted for past tour dates are left as-is (no backfill); newly discovered tour dates group correctly.
- **Rollback:** revert the backend change and the migration; the natural key returns to `(series_id, local_event_date, venue_id)` and `seriesID` derivation to per-(venue,date).

## Open Questions

- **追加公演 anchor hardening:** whether to capture the tour's true 初日 from Gemini's full listing (pre-range-filter) and adopt series identity on it, closing the date-rotation split. Requires verifying that Gemini reliably reports the full tour schedule incl. past dates on the A/B harness.
- **Concurrency:** whether the discovery cron's actual concurrency warrants the advisory-lock hardening or whether the logged rare-double-series is acceptable at launch volume.
- **Cloud SQL PostgreSQL version** confirmed ≥ 15 for `NULLS NOT DISTINCT` (expected, but verify before the migration).
- Backfill/merge of previously scattered SINGLE series for already-discovered tours — out of scope.
