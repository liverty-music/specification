## 1. Protobuf — Entity Layer (specification repo)

- [x] 1.1 Create `proto/liverty_music/entity/v1/series.proto` with `SeriesId`, `SeriesType` enum (`TOUR`, `SINGLE`, `FESTIVAL`), and `Series` message (`id`, `title`, `type`, `source_url`). Add protovalidate constraints and documentation comments.
- [x] 1.2 Rewrite `proto/liverty_music/entity/v1/event.proto` `Event` message to the slimmed shape: `id`, `series_id` (required), `venue`, `local_date`, `start_time`, `open_time`, `merkle_root`. Remove `title`. Keep `EventId` unchanged. Removed field number reserved.
- [x] 1.3 Modify `proto/liverty_music/entity/v1/concert.proto` `Concert` message: remove `Title title`, remove `Url source_url`, replace `ArtistId artist_id` with `repeated Artist performers` (min_items=1), add embedded `Series series` (required). Removed field numbers reserved.
- [x] 1.4 Run `buf format -w` and `buf lint` locally; ensure no STANDARD or COMMENTS rule violations.
- [x] 1.5 Run `buf breaking --against '.git#branch=main'` and confirm the expected breaking diff. The PR will require the `buf skip breaking` label.

## 2. OpenSpec — Spec Sync (specification repo)

- [ ] 2.1 After PR merge and Release, the existing spec at `openspec/specs/event-management/spec.md` will be patched by the archive flow. No manual change here beyond the delta already authored under `openspec/changes/add-series-hierarchy/specs/event-management/spec.md`.

## 3. Database — Atlas Migration (backend repo)

- [x] 3.1 Update `internal/infrastructure/database/rdb/schema/schema.sql` desired-state schema: add `CREATE TYPE series_type`, `CREATE TABLE series`, `CREATE TABLE event_performers`; modify `events` (drop `artist_id`, `title`, `source_url`; add `series_id` NOT NULL FK; replace `uq_events_natural_key` with `(series_id, local_event_date, venue_id)`); modify `concerts` (drop `artist_id`); add `idx_events_series_id`, `idx_event_performers_artist_id`; drop `idx_concerts_artist_id`.
- [x] 3.2 Run `atlas migrate diff --env local add_series_hierarchy` to generate the migration file under `k8s/atlas/base/migrations/`.
- [x] 3.3 Hand-edit the generated migration to prepend `TRUNCATE TABLE events CASCADE;` (Atlas does not infer destructive data ops automatically). Also removed unrelated `DROP INDEX idx_venues_listed_name_admin_area` (schema.sql drift, tracked separately) and stripped `"app"."<name>"` schema qualifiers to match the existing migration convention (`"<name>"`, resolved via search_path).
- [x] 3.4 Add the new migration filename to `k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`.
- [x] 3.5 Run `atlas migrate validate --env local` and `atlas migrate apply --env local` against a fresh local Postgres to confirm the migration applies cleanly. Validate not run (Atlas v1.0.1 `docker://` dev URL incompatible with `search_path=app,public` syntax on this environment); apply succeeded in 309ms, 22 statements OK; schema verified with `\d events`, `\d series`, `\d event_performers`.

## 4. Backend — Entity Layer (backend repo)

- [x] 4.1 Add `internal/entity/series.go` defining `Series` and `SeriesID` types. Mirror the proto shape (no struct tags unless required). Also defined `SeriesType` enum and `SeriesRepository` interface in the same file so Section 5 has an explicit target.
- [x] 4.2 Update `internal/entity/event.go` (or equivalent) to remove `Title`, `SourceURL`, `ArtistID`; add `SeriesID`.
- [x] 4.3 Add `internal/entity/event_performer.go` (or fold into `event.go`) representing the M:N relation. Decide based on existing conventions whether to expose performers as `[]ArtistID` on `Event` or as a separate aggregate.

## 5. Backend — Repository Layer (backend repo)

- [x] 5.1 Add `SeriesRepository` interface and pgx-backed implementation: `Create`, `GetByID`, `List` (filtered by criteria as needed by current callers).
- [x] 5.2 Update `EventRepository`: change `Create`/`Upsert` signatures to accept `SeriesID` and a `[]ArtistID` performers slice; persist `event_performers` rows in the same transaction as the `events` row.
- [x] 5.3 Update `EventRepository.GetByID` / `List*` to JOIN `series` and `event_performers` so callers can populate `Concert` DTOs without N+1.
- [x] 5.4 Update or remove any repository method that read/wrote `events.title`, `events.source_url`, or `events.artist_id` directly.
- [x] 5.5 Update `ConcertRepository` to no longer read/write `concerts.artist_id`. The `concerts` table is now an `event_id`-only placeholder.

## 6. Backend — Use Case Layer (backend repo)

- [x] 6.1 Update `SearchNewConcerts` (auto-discovery) to create a 1:1 `Series` per discovered event during this change (use `SeriesType=SINGLE` as the safe default). Series-grouping intelligence is deferred to the `auto-discovery-series-grouping` follow-up change.
- [x] 6.2 Update `ListConcerts` (or equivalent) to compose the `Concert` DTO from joined `Event` + `Series` + performers.
- [x] 6.3 Update any use case that previously read `Event.Title` or `Event.SourceURL` to source those values from the parent `Series`.

## 7. Backend — Handler / Adapter Layer (backend repo)

- [x] 7.1 Update `ConcertService` handlers to construct the proto `Concert` with embedded `Series series` and `repeated Artist performers`. Field-by-field mapping in `internal/adapter/ipc/`. Partially done: mapper still emits the legacy BSR proto shape (Title / SourceUrl / ArtistId) but sources every value from the new entity locations (Series.Title, Series.SourceURL, Performers[0].ID). The proto-side swap to embedded Series + repeated performers happens in 9.2 once BSR publishes new generated types.
- [x] 7.2 Remove any conversion code that referenced `Event.Title`, `Event.SourceURL`, or `Concert.ArtistId` directly. Done at the entity boundary: every call site now reads from Series / Performers. The mapper still references the legacy proto field names (Title, SourceUrl, ArtistId) by necessity until BSR ships new generated types in 9.2.

## 8. Backend — Tests (backend repo)

- [x] 8.1 Update repository integration tests (`internal/infrastructure/database/rdb/`) for the new `events` columns and `event_performers` rows. Also added two scenario-coverage tests under `concert_repo_test.go`: `TestConcertRepository_CoHeadliners` (M:N performers round-trip) and `TestConcertRepository_DifferentSeriesSameVenueDate` (positive half of the natural-key contract). Both close gaps surfaced by `/opsx:verify`.
- [x] 8.2 Add new integration tests for `SeriesRepository` at `internal/infrastructure/database/rdb/series_repo_test.go`: Create (single / bulk / nil-skip / preset ID / ON CONFLICT DO NOTHING / empty title or type rejection), Get (existing / NotFound / InvalidArgument / source URL absence preserved), ListByIDs (full match / silent omission / empty-slice rejection / SeriesType round-trip).
- [x] 8.3 Update use-case unit tests with new mocks generated by `mockery` after interface changes.
- [x] 8.4 Update handler tests with new `Concert` proto shape.
- [x] 8.5 Run `make check` and confirm all tests pass against a fresh local DB.

## 9. Backend — Dependency Wire-up & Build (backend repo)

- [x] 9.1 After the specification release publishes new generated types to BSR, run `go get buf.build/gen/go/liverty-music/schema/...@<new-version>` and `go mod tidy` in the backend repo. Upgraded `buf.build/gen/go/liverty-music/schema/protocolbuffers/go` and `connectrpc/go` to the v0.41.0-derived BSR builds (commit e7f694dd726b, build 20260524050818) in backend@c5c467e.
- [x] 9.2 Swap the legacy-proto bridge in mapper/concert.go for the real generated types from `buf.build/gen/go/liverty-music/schema/...` (embed Series, expose repeated performers). Re-ran `make check` (green). Also retired the placeholder TODO at the top of `internal/adapter/rpc/concert_handler_test.go` and switched the response-shape assertions to `resp.Msg.Concerts[i].GetSeries().GetTitle()` / `.GetSeries().GetSourceUrl()` / `.GetPerformers()[]`. Added a multi-performer test case (2 performers) at the handler boundary plus a 3-performer "festival lineup" case in the mapper test.
- [x] 9.3 Run `mockery` to regenerate mocks reflecting any interface changes. Run twice — first as part of Section 8 (mock_SeriesRepository.go added in 4a4cf38), again after the 9.2 mapper rewrite (no interface changes, no mock diff).
- [x] 9.4 Run `make check` (lint + tests) end-to-end. Green on backend branch 514-add-series-hierarchy at backend@c5c467e.

## 10. Frontend — Type Migration (frontend repo)

- [x] 10.1 After BSR release, run `npm install @buf/liverty-music_schema.connectrpc_es@<new-version>` to consume the new generated types. Pinned `@buf/liverty-music_schema.bufbuild_es@1.10.0-20260524050818-e7f694dd726b.1` and `@buf/liverty-music_schema.connectrpc_es@1.6.1-20260524050818-e7f694dd726b.2` in frontend@a11f30f (v1.x lineage; the v2.x lineage is not yet published for connectrpc_es, so v1 is the only coherent pair today).
- [x] 10.2 Update any frontend code reading `Concert.title` / `Concert.sourceUrl` / `Concert.artistId` to read from `Concert.series.title` / `Concert.series.sourceUrl` / `Concert.performers`. Done in `src/adapter/rpc/mapper/concert-mapper.ts` (sources title/sourceUrl from `proto.series`, projects `proto.performers[0]` onto the flat entity Concert.artistId — the dashboard entity stays single-artist-flat; multi-performer concerts surface only the lead artist for now) and `src/services/concert-service.ts` (proximity-lane convert loop keys off the first performer). `test/adapter/rpc/mapper/concert-mapper.spec.ts` fixture rewritten to the new proto shape plus a new "projects the first performer when multiple are present" test.
- [x] 10.3 Run `make check` in the frontend repo. Green on frontend branch 514-add-series-hierarchy at frontend@a11f30f.

## 11. PR Coordination

- [x] 11.1 Open the specification PR with the `buf skip breaking` label. Wait for `buf-pr-checks.yml` and review approval before merging. PR #515 opened, six rounds of Claude bot review iteration addressed (final `Claude review` check passed at SUCCESS), merged via merge commit 383341d.
- [x] 11.2 After merge, create a GitHub Release with a SemVer-major tag (since this is a breaking change). The `buf-release.yml` workflow will publish to BSR. Tagged v0.41.0 (minor bump per the existing 0.x repo convention; the team treats 0.x as breaking-allowed) — release notes summarise the schema changes and migration notes.
- [x] 11.3 Monitor `gh run watch` on the BSR release workflow until completion. `Buf BSR Push on Release` workflow run id 26352579947 completed SUCCESS at 2026-05-24T05:08:12Z; `npm view` confirms the matching `e7f694dd726b` BSR build is published for both bufbuild_es (v1 and v2 lineages) and connectrpc_es (v1 lineage).
- [x] 11.4 Open backend and frontend PRs with the new BSR version pinned. Both must reference this OpenSpec change in the PR description (`Refs: #<issue-number>`). Backend PR liverty-music/backend#305 and frontend PR liverty-music/frontend#367 both opened against main with `Refs: liverty-music/specification#514` in the description.

## 12. Post-Merge Verification

- [ ] 12.3 Archive this OpenSpec change with `/opsx:archive` once `openspec status` reports `isComplete=true`.

> Tasks 12.1 (ArgoCD sync confirmation) and 12.2 (dev-env smoke against `api.dev.liverty-music.app`) were removed because the dev environment is currently offline. Add follow-up tasks in a separate change if the environment is restored and an end-to-end smoke is needed before archive.
