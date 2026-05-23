## 1. Protobuf — Entity Layer (specification repo)

- [ ] 1.1 Create `proto/liverty_music/entity/v1/series.proto` with `SeriesId`, `SeriesType` enum (`TOUR`, `SINGLE`, `FESTIVAL`), and `Series` message (`id`, `title`, `type`, `source_url`). Add protovalidate constraints and documentation comments.
- [ ] 1.2 Rewrite `proto/liverty_music/entity/v1/event.proto` `Event` message to the slimmed shape: `id`, `series_id` (required), `venue`, `local_date`, `start_time`, `open_time`, `merkle_root`. Remove `title`. Keep `EventId` unchanged.
- [ ] 1.3 Modify `proto/liverty_music/entity/v1/concert.proto` `Concert` message: remove `Title title`, remove `Url source_url`, replace `ArtistId artist_id` with `repeated Artist performers` (min_items=1), add embedded `Series series` (required).
- [ ] 1.4 Run `buf format -w` and `buf lint` locally; ensure no STANDARD or COMMENTS rule violations.
- [ ] 1.5 Run `buf breaking --against '.git#branch=main'` and confirm the expected breaking diff. The PR will require the `buf skip breaking` label.

## 2. OpenSpec — Spec Sync (specification repo)

- [ ] 2.1 After PR merge and Release, the existing spec at `openspec/specs/event-management/spec.md` will be patched by the archive flow. No manual change here beyond the delta already authored under `openspec/changes/add-series-hierarchy/specs/event-management/spec.md`.

## 3. Database — Atlas Migration (backend repo)

- [ ] 3.1 Update `internal/infrastructure/database/rdb/schema/schema.sql` desired-state schema: add `CREATE TYPE series_type`, `CREATE TABLE series`, `CREATE TABLE event_performers`; modify `events` (drop `artist_id`, `title`, `source_url`; add `series_id` NOT NULL FK; replace `uq_events_natural_key` with `(series_id, local_event_date, venue_id)`); modify `concerts` (drop `artist_id`); add `idx_events_series_id`, `idx_event_performers_artist_id`; drop `idx_concerts_artist_id`.
- [ ] 3.2 Run `atlas migrate diff --env local add_series_hierarchy` to generate the migration file under `k8s/atlas/base/migrations/`.
- [ ] 3.3 Hand-edit the generated migration to prepend `TRUNCATE TABLE events CASCADE;` (Atlas does not infer destructive data ops automatically). Verify the rest of the diff matches the schema changes above.
- [ ] 3.4 Add the new migration filename to `k8s/atlas/base/kustomization.yaml` under `configMapGenerator.files`.
- [ ] 3.5 Run `atlas migrate validate --env local` and `atlas migrate apply --env local` against a fresh local Postgres to confirm the migration applies cleanly.

## 4. Backend — Entity Layer (backend repo)

- [ ] 4.1 Add `internal/entity/series.go` defining `Series` and `SeriesID` types. Mirror the proto shape (no struct tags unless required).
- [ ] 4.2 Update `internal/entity/event.go` (or equivalent) to remove `Title`, `SourceURL`, `ArtistID`; add `SeriesID`.
- [ ] 4.3 Add `internal/entity/event_performer.go` (or fold into `event.go`) representing the M:N relation. Decide based on existing conventions whether to expose performers as `[]ArtistID` on `Event` or as a separate aggregate.

## 5. Backend — Repository Layer (backend repo)

- [ ] 5.1 Add `SeriesRepository` interface and pgx-backed implementation: `Create`, `GetByID`, `List` (filtered by criteria as needed by current callers).
- [ ] 5.2 Update `EventRepository`: change `Create`/`Upsert` signatures to accept `SeriesID` and a `[]ArtistID` performers slice; persist `event_performers` rows in the same transaction as the `events` row.
- [ ] 5.3 Update `EventRepository.GetByID` / `List*` to JOIN `series` and `event_performers` so callers can populate `Concert` DTOs without N+1.
- [ ] 5.4 Update or remove any repository method that read/wrote `events.title`, `events.source_url`, or `events.artist_id` directly.
- [ ] 5.5 Update `ConcertRepository` to no longer read/write `concerts.artist_id`. The `concerts` table is now an `event_id`-only placeholder.

## 6. Backend — Use Case Layer (backend repo)

- [ ] 6.1 Update `SearchNewConcerts` (auto-discovery) to create a 1:1 `Series` per discovered event during this change (use `SeriesType=SINGLE` as the safe default). Series-grouping intelligence is deferred to the `auto-discovery-series-grouping` follow-up change.
- [ ] 6.2 Update `ListConcerts` (or equivalent) to compose the `Concert` DTO from joined `Event` + `Series` + performers.
- [ ] 6.3 Update any use case that previously read `Event.Title` or `Event.SourceURL` to source those values from the parent `Series`.

## 7. Backend — Handler / Adapter Layer (backend repo)

- [ ] 7.1 Update `ConcertService` handlers to construct the proto `Concert` with embedded `Series series` and `repeated Artist performers`. Field-by-field mapping in `internal/adapter/ipc/`.
- [ ] 7.2 Remove any conversion code that referenced `Event.Title`, `Event.SourceURL`, or `Concert.ArtistId` directly.

## 8. Backend — Tests (backend repo)

- [ ] 8.1 Update repository integration tests (`internal/infrastructure/database/rdb/`) for the new `events` columns and `event_performers` rows.
- [ ] 8.2 Add new integration tests for `SeriesRepository`.
- [ ] 8.3 Update use-case unit tests with new mocks generated by `mockery` after interface changes.
- [ ] 8.4 Update handler tests with new `Concert` proto shape.
- [ ] 8.5 Run `make check` and confirm all tests pass against a fresh local DB.

## 9. Backend — Dependency Wire-up & Build (backend repo)

- [ ] 9.1 After the specification release publishes new generated types to BSR, run `go get buf.build/gen/go/liverty-music/schema/...@<new-version>` and `go mod tidy` in the backend repo.
- [ ] 9.2 Swap any placeholder type aliases (if used during parallel development) for the real generated types from `buf.build/gen/go/liverty-music/schema/...`.
- [ ] 9.3 Run `mockery` to regenerate mocks reflecting any interface changes.
- [ ] 9.4 Run `make check` (lint + tests) end-to-end.

## 10. Frontend — Type Migration (frontend repo)

- [ ] 10.1 After BSR release, run `npm install @buf/liverty-music_schema.connectrpc_es@<new-version>` to consume the new generated types.
- [ ] 10.2 Update any frontend code reading `Concert.title` / `Concert.sourceUrl` / `Concert.artistId` to read from `Concert.series.title` / `Concert.series.sourceUrl` / `Concert.performers`.
- [ ] 10.3 Run `make check` in the frontend repo.

## 11. PR Coordination

- [ ] 11.1 Open the specification PR with the `buf skip breaking` label. Wait for `buf-pr-checks.yml` and review approval before merging.
- [ ] 11.2 After merge, create a GitHub Release with a SemVer-major tag (since this is a breaking change). The `buf-release.yml` workflow will publish to BSR.
- [ ] 11.3 Monitor `gh run watch` on the BSR release workflow until completion.
- [ ] 11.4 Open backend and frontend PRs with the new BSR version pinned. Both must reference this OpenSpec change in the PR description (`Refs: #<issue-number>`).

## 12. Post-Merge Verification

- [ ] 12.1 Confirm ArgoCD has synced the new schema (Atlas operator applies migration in dev).
- [ ] 12.2 Smoke-test `ConcertService` against `api.dev.liverty-music.app` using a captured Zitadel JWT; verify the response carries the embedded `Series` and `performers[]`.
- [ ] 12.3 Archive this OpenSpec change with `/opsx:archive` once `openspec status` reports `isComplete=true`.
