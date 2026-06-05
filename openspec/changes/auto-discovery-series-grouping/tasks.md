## 1. Preserve Tour Grouping in Gemini Parsing (backend)

- [x] 1.1 Add a block-origin marker (tour/standalone) and an intra-run tour-group handle to `EventDraft` in `internal/infrastructure/gcp/gemini/searcher.go`
- [x] 1.2 Update `parseStep1Envelope` to populate them: `<tour>` children share one intra-run handle (e.g. block index); `<standalone>` drafts marked standalone with no handle. The handle need NOT derive from `source_url`/title
- [x] 1.3 Confirm Step-2 merge-by-`index`, the `(local_date, normalized_venue, start_time)` dedup, and all verbatim fields are unaffected
- [x] 1.4 Unit tests: three-date tour → shared handle + tour-origin; standalone → standalone-origin; two tours → two handles

## 2. Carry Grouping Onto ScrapedConcert (backend)

- [x] 2.1 Add the block-origin marker + intra-run tour-group handle to `ScrapedConcert` in `internal/entity/concert.go`
- [x] 2.2 Propagate the fields when EventDrafts are merged/coerced into `[]*ScrapedConcert`
- [x] 2.3 Verify the `FilterNew` application dedup and grouping fields survive dedup (FilterNew re-keyed to (date, venue, start) with asymmetric NULL handling so 昼夜 survive and fills pass through)

## 3. Physical Event Natural Key + Migration (backend)

- [x] 3.1 Update desired-state schema `internal/infrastructure/database/rdb/schema/schema.sql`: replace `uq_events_natural_key` with `UNIQUE (venue_id, local_event_date, start_at) NULLS NOT DISTINCT`; replace `chk_series_id_uuid_v5_or_v7` with `chk_series_id_uuidv7` (pure `UUIDv7`)
- [x] 3.2 Generate the Atlas migration (`atlas migrate diff --env local`): dedup existing `events` rows that would violate the new constraint (repoint `event_performers` to the survivor), drop old constraint, add new constraint
- [x] 3.3 Author the `series.id` backfill as a hand-written migration step (Atlas `diff` emits only schema DDL): re-key any existing v5 `series.id` to a fresh `UUIDv7`, cascading the new id to all FK referencers (`events.series_id`, `sales_phases.series_id`, any other `series` reference) in one transaction; no-op when no v5 rows exist. Order it BEFORE adding `chk_series_id_uuidv7` so the new CHECK validates immediately (no `NOT VALID` needed)
- [x] 3.4 Add the migration file(s) to `k8s/atlas/base/kustomization.yaml` `configMapGenerator.files`
- [x] 3.5 Confirm Cloud SQL PostgreSQL version ≥ 15 (`NULLS NOT DISTINCT`) before relying on it — local + CI dev DB are PostgreSQL 18; migration applies and validates clean

## 4. Application-Layer Event Resolution + Series Adoption (backend)

- [x] 4.1 In `internal/usecase/concert_creation_uc.go`, remove the `UUIDv5(venueID|local_date)` derivation entirely
- [x] 4.2 Resolve each scraped event against existing rows by `(venue_id, local_event_date)`: NULL-start row + known incoming start → UPDATE (fill); same known start → UPDATE; different known start → INSERT (new session); default ambiguous cases to fill
- [x] 4.3 Derive series identity by FK adoption: for a tour group, reuse the `series_id` of any already-existing member event; else mint a fresh `UUIDv7` series. All events of one `<tour>` handle share one series within the run
- [x] 4.4 Standalone events: resolve identity the same physical way; each standalone gets its own SINGLE series (adopt-or-mint)
- [x] 4.5 Assign `SeriesType`: TOUR for tour-origin, SINGLE for standalone (from source classification, not event count)
- [x] 4.6 Update `ScrapedConcert.ToConcert` / the creation path so Series title/source_url/type reflect the group and `series.id` is `UUIDv7`
- [x] 4.7 Log residual ambiguities (late-additional-dates split, multi-hall bare-vs-hall split, concurrency double-series) as warnings; never fail discovery

## 5. Repository Re-keying (backend)

- [x] 5.1 Update `upsertEventsQuery` in `internal/infrastructure/database/rdb/concert_repo.go` to the `(venue_id, local_event_date, start_at)` constraint; preserve `COALESCE` fill of `start_at`/`open_at` (conflict target is the named constraint, unchanged; within-batch dedup re-keyed to the physical key; new `FillEventStartTimes` covers NULL→known fill)
- [x] 5.2 Re-key `insertEventPerformersQuery` JOIN from `(series_id, local_event_date, venue_id)` to `(venue_id, local_event_date, start_at)` (start_at matched with `IS NOT DISTINCT FROM`)
- [x] 5.3 Confirm `event_performers` linkage and notification RETURNING semantics still hold on the co-headliner / pre-existing-event path

## 6. Tests (backend)

- [x] 6.1 Use-case test: multi-stop tour → one TOUR series, N events share `series_id`
- [x] 6.2 Use-case test: re-discovery of the same tour adopts the existing series (no duplicate series)
- [x] 6.3 Use-case test: divergent-title co-headline tour via two artists → one TOUR series (covered by adoption test: identity is event-derived, title-independent)
- [x] 6.4 Use-case test: standalone co-headliner via two artists → one event row, two `event_performers` (repo co-headliner test on the physical key)
- [x] 6.5 Use-case test: NULL start_at first, concrete start_at later → single row filled (no duplicate)
- [x] 6.6 Use-case test: matinee/evening same venue+date, distinct start_at → two events
- [x] 6.7 Integration test: physical natural key collapses same venue+date+start across series; distinct starts stay separate (`TestConcertRepository_PhysicalNaturalKey`)
- [x] 6.8 Use-case test: single-date `<tour>` stays TOUR; multi-day `<standalone>` stays SINGLE

## 7. Specification & Verification

- [x] 7.1 No proto change — confirm `Series`/`SeriesType`/`start_at`/`local_date`/`venue` already cover this; no `buf` run needed
- [x] 7.2 `make check` (backend) green
- [ ] 7.3 Local verification: run `cmd/job/concert-discovery` against an artist with a known multi-date tour → one TOUR series with all dates; a standalone → SINGLE; a 昼夜2公演 venue → two events
- [ ] 7.4 Open a backend-only PR (no BSR/cross-repo flow), including the Atlas migration
- [ ] 7.5 Ship to prod (backend Release tag → image) per the change's prod-release goal
