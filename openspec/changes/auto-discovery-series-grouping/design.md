## Context

`add-series-hierarchy` introduced the `Series` parent entity and the `SeriesType` enum (TOUR/SINGLE/FESTIVAL) but shipped a 1-`Series`-per-`Event` fallback, explicitly deferring real grouping to this change. Today `concert_creation_uc.go` derives `seriesID = UUIDv5(venueID|local_date)` and sets `SeriesType = SINGLE` for every discovered date, so a multi-stop tour fragments into many single-row series.

Two facts from codebase exploration drive the design:

1. **Gemini already groups tours.** Step 1 emits an `<extracted>` envelope with `<tour>` blocks (each `<title>`, `<source_url>`, and multiple `<event>` children) and `<standalone>` blocks (one `<event>`). But `parseStep1Envelope` flattens this into a flat `[]EventDraft`, discarding which events belonged to the same tour — only the shared `Title`/`SourceURL` survive as an indirect trace.

2. **The co-headliner dedup lives only in the standalone path.** The current per-(venue,date) `seriesID` is deliberately artist-independent so that co-headliners discovered via separate per-artist searches dedup onto one event row (the events natural key embeds `series_id`). Crucially, the Gemini prompts segregate by role: the tour slice extracts "%s のツアー" from the artist's own official site and **excludes festivals and standalones**; the standalone slice extracts solo/FC/2–4-act 対バン and **excludes festivals and tours**; 10+-act festivals are out of scope entirely. So co-headliner events are always **standalones**, never tours.

This means a tour-scoped `seriesID` never intersects the co-headliner dedup path, as long as standalones keep their per-(venue,date) key. That removes the only real obstacle to grouping.

## Goals / Non-Goals

**Goals:**
- Persist a multi-stop tour as a single `Series` (SeriesType=TOUR) shared by all its events.
- Preserve Gemini's existing tour grouping through the pipeline instead of re-deriving it.
- Keep standalone (incl. co-headliner) dedup behavior exactly as today.
- Backend-only: no proto change, no DB migration.

**Non-Goals:**
- Grouping standalones or festivals into series.
- Reconciling a tour discovered via two artists with divergent titles into one series.
- Changing the events natural key or decoupling event identity from `series_id`.
- Fuzzy title matching against previously persisted series (a future hardening).

## Decisions

### Decision 1: Preserve Gemini's tour grouping rather than re-derive it
Carry a tour-group identity and a tour/standalone marker from `parseStep1Envelope` onto `EventDraft`, then onto `ScrapedConcert`. The authoritative grouping is what Gemini emitted (`<tour>` vs `<standalone>`); re-deriving it downstream (e.g., by clustering on title) would be lossy and redundant.
- **Alternative considered**: Re-cluster flat `EventDraft`s by `(Title, SourceURL)` in concert creation. Rejected — `(Title, SourceURL)` is a weaker signal than the explicit block boundary, and standalones can share neither, so the block marker is needed regardless.

### Decision 2: Tour-scoped deterministic seriesID for tours; unchanged (venue,date) for standalones
- **Tour events**: all events in one `<tour>` group share one `seriesID`, derived deterministically so re-discovery is idempotent — `UUIDv5(namespace, normalized tour key)` where the tour key is the tour's `source_url` (falling back to artist-scoped normalized title when `source_url` is absent). `SeriesType = TOUR`.
- **Standalone events**: keep `seriesID = UUIDv5(venueID|local_date)`, `SeriesType = SINGLE` — preserving the artist-independent cross-artist dedup the current code relies on.
- **Alternative considered**: Use the tour title alone as the key. Rejected — titles vary across runs/sites; `source_url` is the stabler tour identity, and the existing envelope already carries it per tour.

### Decision 3: SeriesType is assigned from the Gemini block, not inferred from event count
A `<tour>` block yields TOUR even if only one of its dates falls in range; a `<standalone>` yields SINGLE even if multi-day. Trusting the source classification avoids fragile count-based heuristics.

### Decision 4: No change to the events natural key or persistence dedup
The natural key `(series_id, local_event_date, venue_id)` and the `ON CONFLICT` UPSERT stay as-is. For tours, the shared tour `series_id` plus `(date, venue)` still uniquely identifies each stop. The application dedup key `(local_date, listed_venue_name, start_at)` is unchanged. Co-headliner linkage via `event_performers` is untouched.

## Risks / Trade-offs

- **Co-headline multi-venue tour with divergent titles across two artists** → two TOUR series for one real tour. Mitigation: keying on `source_url` collapses them when both sites point at the same tour page; otherwise accepted as a rare duplicate (no data loss), logged. Future: fuzzy series reconciliation.
- **Same physical event classified as a tour stop by artist A and a standalone co-bill by artist B** → two event rows (tour `series_id` vs venue|date `series_id`). Mitigation: rare; accepted, logged. Hardening (venue+date reconciliation) is out of scope.
- **Gemini misclassifies a one-off as a `<tour>`** → a TOUR series with one event. Low harm (still a valid series); SINGLE vs TOUR is cosmetic for a single date.
- **`source_url` missing on a tour block** → fall back to artist-scoped normalized title for the key; slightly less stable but still deterministic per run.

## Migration Plan

- Pure behavior change in the discovery write path; additive fields on internal structs only. No proto change, no DB migration, no cross-repo BSR flow.
- Existing SINGLE series already persisted for past tour dates are left as-is (no backfill); newly discovered tour dates group correctly. A one-off backfill is out of scope.
- Rollback: revert the backend change; the seriesID derivation returns to per-(venue,date) for all events.

## Open Questions

- Whether to backfill/merge previously scattered SINGLE series for already-discovered tours (currently out of scope).
- Whether `source_url` is reliably present on tour blocks in practice, or whether the title fallback dominates (informs key stability; verify against the A/B harness).
