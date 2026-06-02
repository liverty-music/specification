## 1. Preserve Tour Grouping in Gemini Parsing (backend)

- [ ] 1.1 Add tour-origin marker + tour-group identity fields to `EventDraft` in `internal/infrastructure/gcp/gemini/searcher.go`
- [ ] 1.2 Update `parseStep1Envelope` to populate them: `<tour>` children share a group identity derived from the tour's `source_url` (fallback: title); `<standalone>` drafts marked standalone with no group identity
- [ ] 1.3 Confirm Step-2 merge-by-`index` and all existing verbatim fields are unaffected
- [ ] 1.4 Unit tests: three-date tour → shared identity + tour-origin; standalone → standalone-origin; two tours → two identities

## 2. Carry Grouping Onto ScrapedConcert (backend)

- [ ] 2.1 Add the tour-origin marker + tour-group identity to `ScrapedConcert` in `internal/entity/concert.go`
- [ ] 2.2 Propagate the fields when EventDrafts are merged/coerced into `[]*ScrapedConcert`
- [ ] 2.3 Verify the `(local_date, listed_venue_name, start_at)` application dedup key in `FilterNew` is unchanged and grouping fields survive dedup

## 3. Tour-Grouped Series Creation (backend)

- [ ] 3.1 In `internal/usecase/concert_creation_uc.go`, branch seriesID derivation: tour-origin → one deterministic `UUIDv5(source_url | artist-scoped normalized title)` shared per tour group; standalone → existing `UUIDv5(venueID|local_date)`
- [ ] 3.2 Assign `SeriesType`: TOUR for tour-origin, SINGLE for standalone (from source classification, not event count)
- [ ] 3.3 Ensure one `Series` row per tour group is added to the series batch (deduped within the batch by tour seriesID), all its events referencing that `series_id`
- [ ] 3.4 Update `ScrapedConcert.ToConcert` (or the creation path) so Series title/source_url/type reflect the group
- [ ] 3.5 Log residual grouping ambiguities (divergent-title co-headline tour, tour-stop-vs-standalone collision) as warnings; never fail discovery
- [ ] 3.6 Confirm no change to the events natural key, `ON CONFLICT` UPSERT, or `event_performers` linkage

## 4. Tests (backend)

- [ ] 4.1 Use-case test: multi-stop tour → one TOUR series, N events share series_id
- [ ] 4.2 Use-case test: re-discovery of the same tour is idempotent (no duplicate series)
- [ ] 4.3 Use-case test: standalone co-headliner discovered via two artists → one event row, two `event_performers`, SINGLE series unchanged
- [ ] 4.4 Use-case test: single-date `<tour>` block stays TOUR; multi-day `<standalone>` stays SINGLE

## 5. Specification & Verification

- [ ] 5.1 No proto change required — confirm `Series`/`SeriesType` already cover TOUR; no `buf` run needed
- [ ] 5.2 `make check` (backend) green
- [ ] 5.3 Local verification: run `cmd/job/concert-discovery` against an artist with a known multi-date tour → one TOUR series with all dates; a standalone → SINGLE
- [ ] 5.4 Open a backend-only PR (no BSR/cross-repo flow)
