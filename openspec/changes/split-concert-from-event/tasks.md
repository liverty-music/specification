## 1. Specification prerequisites

- [ ] 1.1 In the plan PR, add a commit before the change that moves the main spec `components/adapter/organizer/api/rpc/concert` to `components/adapter/organizer/api/rpc/series` (design D8):
  - Reword its Purpose to "the organizer Series service boundary".
  - Move `redesign-organizer-console`'s delta directory at that path to the new path.
  - Put the mapping table (old path → new path) in the commit message.
  - Verify `openspec validate split-concert-from-event --strict` and `openspec validate redesign-organizer-console --strict` both pass, with no "target spec does not exist" notice.
- [ ] 1.2 Open two issues in liverty-music/specification and verify both are open. Link them from design.md Non-Goals.
  - One for the sales-phase notification link `/concerts/<id>`, which cannot reach an event that is not in the fan's dashboard list. Cite `sales_phase_copy.go:78` and `dashboard-route.ts` `resolvePendingDeepLink`.
  - One for `stories/complete-onboarding`, which still describes polling after a `SearchNewConcerts` RPC the frontend never calls and this change removes.

## 2. Database (backend, design D6)

- [ ] 2.1 Run read-only checks in prod through the db-proxy runbook and record the results in design.md D6.
  - The count of `event_performers` rows without a `concerts` row must be 0.
  - Record the actual constraint names of `event_performers` (`pg_constraint`).
  - If the count is not 0, stop and add a backfill step to D6 before 2.2.
- [ ] 2.2 Rename `event_performers` to `concert_artists` in `schema.sql`, with the foreign key on `concerts(event_id)` and the table and column comments.
  - Hand-edit the generated migration to `RENAME` with the constraint names from 2.1, run `atlas migrate hash`, and add the file to `k8s/atlas/base/kustomization.yaml`.
  - Verify `atlas migrate apply --env local` succeeds on a database with existing rows, and that `make lint-schema` passes.
- [ ] 2.3 Point every SQL that reads or writes `event_performers` at `concert_artists`: `concert_repo.go`, `series_repo.go`, the organizer delete and the test cleanup list.
  - Verify the `components/entity/concert/create` integration tests pass: New slot, Existing slot keeps its id, Known open time is not overwritten, Unknown open time is filled, Different start time is a new event, Co-headliner found later, Repeated create, Unknown series, No performer.
  - Verify the Concert read, delete-and-suppress and Organizer.Delete integration tests still pass.
- [ ] 2.4 Update the expected grants in `migration_grants_integration_test.go`: `concert_artists` gets INSERT for `organizer-console-api`, and `event_performers` leaves. Verify the test passes against the migrated local database.

## 3. Proto (specification → BSR, design D1, D2, D5, D7)

- [ ] 3.1 Change the entity messages:
  - `entity.v1.Event` gains `listed_venue_name`.
  - `entity.v1.Concert` becomes `{ Event event; repeated ArtistId artist_ids }`, with at least 1 and unique ids, and fields 1–12 reserved.
  - Every doc comment states that a Concert's Series and Artists come in the response's `series` and `artists` lists.
  - Verify `buf lint` and `buf format -d` pass.
- [ ] 3.2 In the fan `ConcertService`, add `repeated Series series` and `repeated Artist artists` to the Get, List, ListBySeries, ListByFollower, ListByArtists and ListByLocation responses, and remove `SearchNewConcerts` with its messages. Verify `buf lint` passes, and that `buf breaking` reports only the intended breaks.
- [ ] 3.3 Move the organizer service to `rpc/organizer/series/v1` as `SeriesService`, with the same eight RPCs.
  - Create, Update, Publish, Cancel and AttachMedia return `{ series, concerts, artists }`, and List returns `{ repeated series, concerts, artists }`.
  - Remove `AuthoredConcert`, and add the side lists to the admin `ConcertService.List` response.
  - Verify `buf lint` passes.
- [ ] 3.4 Open the specification PR citing this change, merge it and cut a Release. Verify `buf-release.yml` succeeds and the BSR Go and ES packages carry the new `Concert` and `SeriesService`.

## 4. Entity (components/entity/event, components/entity/concert)

- [ ] 4.1 Rename `entity.Concert.Performers` to `Artists` in the backend.
  - Verify unit tests carrying `@spec` markers pass for "Title comes from the series", "Concert id is its event id" and "Co-headlined concert".
  - Verify the existing Concert entity tests (proximity, earliest, visibility) still pass.

## 5. Fan boundary (components/adapter/fan/api/rpc/concert, design D2, D3, D7)

- [ ] 5.1 Add the Series cover join to the Concert reads (design D3). Drop the `Series.Get` replacement from `ConcertUseCase.Get` and `ListBySeries`, keeping their event-page check.
  - Verify the `components/usecase/concert/get` tests pass: Published public concert, Cancelled series, Unknown id, Unlisted series, Discovered concert, Store unavailable.
  - Verify the `components/usecase/concert/list-by-series` tests still pass.
- [ ] 5.2 Build the `series` and `artists` side lists in the mapper (each distinct id once, first-seen order) for every fan response that returns Concerts. The fan `SeriesToProto` always sets the cover when the Series has one.
  - Verify handler tests with `@spec` markers pass: Venue without coordinates, Artist without concerts, First-party concert in a list, Discovered concert in a list, Tour in one list, Cover image in a list.
- [ ] 5.3 Remove the `SearchNewConcerts` handler and its `FanPublicProcedures()` entry.
  - Verify boundary tests with `@spec` markers pass: Guest lists concerts of chosen artists, Guest asks for followed artists' concerts, Guest opens an event page, Guest lists the dates of a series, Too many artists, Range backwards, Event page without an id.
  - Verify `ConcertUseCase.SearchNewConcerts` still runs from `cmd/job/concert-discovery` (the job's existing test).

## 6. Request timeout (components/infrastructure/fan/api/server/request-timeout, design D7)

- [ ] 6.1 Remove `ServerSettings.ConcertHandlerTimeout`, `SERVER_CONCERT_HANDLER_TIMEOUT` and the per-service timeout in `provider.go`. Verify tests with `@spec` markers pass for "Concert call over the limit" (30 s) and "Other call over the limit".

## 7. Admin boundary (components/adapter/admin/api/rpc/concert)

- [ ] 7.1 Return the side lists from the admin `ConcertService.List`. Verify a handler test with an `@spec` marker passes for "Two approved concerts of one series", and the existing admin concert tests still pass.

## 8. Organizer boundary (components/adapter/organizer/api/rpc/series, design D5)

- [ ] 8.1 Move the organizer handler to `SeriesService`, register it in the organizer handler list in `internal/di/provider.go`, and return `{ series, concerts, artists }`. A DRAFT Series' DraftEvents become Concerts carrying the draft performers.
  - Move the existing `@spec components/adapter/organizer/api/rpc/concert` markers in `organizer_concert_handler_test.go` to the new path.
  - Verify handler tests with `@spec` markers pass: Operator of an active Organizer lists concerts, Provisioning Organizer, Deactivated Organizer, Draft without events, New token, Tour with one performer, Draft series.
- [ ] 8.2 Open the backend PR citing this change (after 3.4), covering groups 2 and 4–8. Get `make check` and CI green and merge. Do not release yet (see 9.3).

## 9. Frontend (fan, admin, organizer)

- [ ] 9.1 Fan app: read the new shape through one shared step that indexes `series` and `artists` by id and turns each Concert into its view model. Use it in `ConcertStore` (dashboard, welcome), the event page and the tickets page.
  - Verify the unit tests of `concert-store`, `event-route`, `tickets-route` and `dashboard-route` pass.
  - Verify the e2e functional fixtures of the ConcertService shape are updated and pass.
- [ ] 9.2 Admin and organizer apps:
  - Move `admin/approved-concerts` to the side lists.
  - Move the organizer console client to `SeriesService`, grouping `concerts` by `event.series_id` into one page per Series.
  - Verify their unit tests pass and that `make check` passes.
- [ ] 9.3 Open the frontend PR citing this change, merge it, then release the backend and the frontend together. Verify:
  - the prod pins move;
  - `e2e/prod/open-a-shared-event-link` (guest and authenticated) passes against prod;
  - the dashboard, the admin approved-concerts list and the organizer concert list render in prod.

## 10. Cloud provisioning

- [ ] 10.1 Remove `SERVER_CONCERT_HANDLER_TIMEOUT` from the fan-api ConfigMap (prod and dev overlays) after 9.3. Verify `make lint-k8s` passes and fan-api rolls out healthy in prod.

## 11. Changes in flight (specification store)

- [ ] 11.1 Rewrite the artifacts of the following changes to the new names: `concert_artists`, organizer `SeriesService`, `Concert { event, artist_ids }`, and responses with side lists.
  - `restructure-event-publishing`
  - `redesign-organizer-console`
  - `migrate-discovered-sales`
  - `unify-ticket-sales`
  - `organizer-event-authoring-extensions`
  - Verify `openspec validate <change> --strict` passes for each.
