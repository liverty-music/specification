## Why

The `add-series-hierarchy` change shipped a 1-`Series`-per-`Event` fallback and explicitly deferred real tour grouping to a follow-up named `auto-discovery-series-grouping`. Today every discovered concert date becomes its own `Series` (SeriesType=SINGLE), so a multi-stop tour is scattered across many single-row series. This blocks any series-level feature (sales timeline, tour-level UI, merch) because there is no single object representing "the tour". The Gemini searcher already groups dates under a `<tour>` block, but that grouping is flattened and lost during parsing — we just need to preserve and persist it.

## What Changes

- Preserve the tour grouping that Gemini Step 1 already produces: stop flattening the `<tour>`→events relationship in `parseStep1Envelope`, and carry a tour-group identity (and a tour/standalone marker) through `EventDraft` → `ScrapedConcert`.
- In concert creation, derive a single deterministic `Series` per tour group (SeriesType=TOUR) shared by all its events, instead of one SINGLE series per date.
- Keep standalone concerts on the existing per-`(venue, date)` deterministic `seriesID` (SeriesType=SINGLE). This is intentional: standalones include 2–4 act co-headliner bills that two followed artists may discover separately, and the venue+date key preserves their cross-artist event dedup. Tours are extracted from a single artist's own official site (festivals excluded), so a tour-scoped `seriesID` does not intersect the co-headliner dedup path.
- No proto or database schema change: the `Series` entity, `SeriesType` enum, and the events natural key `(series_id, local_event_date, venue_id)` are unchanged. Only the seriesID derivation and SeriesType assignment during discovery change.

## Capabilities

### New Capabilities
- `auto-discovery-series-grouping`: The discovery-time grouping behavior — deriving one deterministic TOUR `Series` per tour group shared by all its events, assigning SeriesType, and leaving standalones on the existing per-(venue,date) SINGLE path. This replaces the 1:1 SINGLE fallback deferred by `add-series-hierarchy`.

### Modified Capabilities
- `gemini-grounded-extract-and-coerce`: `parseStep1Envelope` SHALL no longer discard the tour grouping; each `EventDraft` SHALL carry which tour group (if any) it belongs to and whether it originated from a `<tour>` or `<standalone>` block, so the grouping survives into persistence.

<!-- event-management is intentionally NOT listed: its requirements already permit TOUR series
     (SERIES_TYPE_TOUR, "Series owns shared metadata" scenario) and the events natural key
     (series_id, local_event_date, venue_id) is unchanged. The "typically SINGLE" wording was an
     implementation detail, not a requirement, so no delta is needed. auto-concert-discovery's
     requirements (scheduling, circuit-breaker, DI) are likewise unchanged. -->


## Impact

- **specification**: No proto change. Delta specs only for the capabilities above.
- **backend**: `internal/infrastructure/gcp/gemini/searcher.go` (`parseStep1Envelope`, `EventDraft` gains tour-group + tour/standalone fields), `internal/entity/concert.go` (`ScrapedConcert` gains the same, `ToConcert`/SeriesType selection), `internal/usecase/concert_creation_uc.go` (seriesID derivation branches on tour vs standalone; SeriesType assignment), plus unit tests. No DB migration; `series` table and the events natural key are untouched.
- **No cross-repo BSR flow** (no proto change) — backend-only PR.
- **Known limitations (accepted, logged)**: a genuine co-headline multi-venue tour discovered via two artists with divergent titles may yield two TOUR series; an event that is a tour stop for one artist and a standalone co-bill for another may produce two rows. Both are rare and produce duplicate rows, not data loss; hardening (venue+date reconciliation) is out of scope.
