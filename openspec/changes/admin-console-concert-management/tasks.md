## 1. Specification & Proto (specification repo)

- [x] 1.1 Rename `proto/liverty_music/rpc/admin/v1/concert_moderation_service.proto` → `concert_service.proto` (git mv); rename `service ConcertModerationService` → `service ConcertService`; update package-level and service doc comments to describe admin concert management (not just moderation)
- [x] 1.2 Rename methods to bare verbs: `ListPendingConcerts`→`ListPending`, `ApproveConcert`→`Approve`, `RejectConcert`→`Reject` (keep request/response message names coherent, e.g. `ListPendingRequest`/`Response`); preserve existing field shapes and validation
- [x] 1.3 Add `List` (request: empty; response: `repeated` published concert with event id, performer, title, local date, start time, listed/resolved venue) and `Delete` (request: required `entity.v1.EventId`; response: empty) with doc comments stating cascade + unconditional semantics and the `INVALID_ARGUMENT`/idempotent-on-missing error contract
- [x] 1.4 Run `buf lint` + `buf format`; run `buf breaking` and confirm the only breaking deltas are the service rename + the three method renames (no unexpected message/field breakage)
- [ ] 1.5 Open the specification PR with the proto change + this OpenSpec change; merge after review and CI (`buf-pr-checks.yml`) pass
- [ ] 1.6 Publish a GitHub Release (tag `vX.Y.Z`) to trigger `buf-release.yml` → BSR push; monitor `buf-release.yml` to success

## 2. Backend — use-case merge & interface segregation (prepared in parallel, finalized after BSR gen)

- [ ] 2.1 Merge `ConcertApprovalUseCase` logic into the concrete `concertUseCase`: add `rejectedConcertRepo` + `seriesRepo` to the struct and `NewConcertUseCase` constructor; move `ListPending`, `Approve`, `Reject` method bodies over; delete `concert_approval_uc.go` and the `ConcertApprovalUseCase` interface + its mock
- [ ] 2.2 Define the segregated admin use-case interface (e.g. `AdminConcertUseCase`) exposing `ListPending`/`Approve`/`Reject`/`List`/`Delete`; keep the existing read-only `ConcertUseCase` interface for the consumer handler unchanged; assert `concertUseCase` satisfies both; regenerate mocks
- [ ] 2.3 Add `ConcertRepository.List(ctx)` returning all published concerts hydrated like the other list methods; implement against the existing concert/event/venue/performer joins
- [ ] 2.4 Add `ConcertRepository.Delete(ctx, eventID)` as a single `DELETE FROM events WHERE id = $1` relying on FK cascade; return success when zero rows matched (idempotent); add a focused integration test asserting cascade removes dependent rows
- [ ] 2.5 Implement use-case `List` (passthrough to repo) and `Delete` (validate id → repo delete; map missing→success, malformed→`INVALID_ARGUMENT`)

## 3. Backend — handler & DI rename (finalized after BSR gen)

- [ ] 3.1 Bump the generated schema package to `vX.Y.Z`; `go mod tidy`
- [ ] 3.2 Rename `ConcertModerationHandler` → `AdminConcertHandler`; update it to the regenerated `ConcertService` method set (`ListPending`/`Approve`/`Reject` renamed, add `List`/`Delete`); depend on the `AdminConcertUseCase` interface
- [ ] 3.3 Update admin-server DI registration to the regenerated `adminv1connect` `ConcertServiceHandler` constructor; wire the merged use case + new repos; remove the deleted approval use-case provider
- [ ] 3.4 Update/extend unit tests (handler + use case): `List` returns published only, `Delete` cascades/idempotent/`INVALID_ARGUMENT`, approval methods still pass under new names; `make check` green

## 4. Frontend — admin approved-concerts route (finalized after BSR gen)

- [ ] 4.1 Bump the BSR-generated package to the version carrying `admin.v1.ConcertService`; rename `admin/services/concert-moderation-client.ts` → `concert-client.ts` and re-point it at the regenerated `ConcertService` client; update method calls to the bare-verb names and add `list()` / `delete(eventId)`
- [ ] 4.2 Add `admin/approved-concerts/` route + view model: load via `list()`, group rows by performing artist client-side, render per-artist sections
- [ ] 4.3 Add a per-row delete control with a confirm step that issues `delete(eventId)` only on confirmation; on success remove the row, on failure surface a per-row error
- [ ] 4.4 Register the route in the admin shell/nav; add unit tests (grouping, confirm-gated delete, error surfacing); `make check` green

## 5. Ship to production (coordinated cutover)

- [ ] 5.1 Open the backend PR only after the package upgrade + rename compile and `make check` pass locally; merge after review/CI
- [ ] 5.2 Open the frontend PR likewise; merge after review/CI
- [ ] 5.3 Publish the backend GitHub Release (tag `vX.Y.Z`) to retag the dev AR image to prod; confirm ArgoCD syncs the new backend image
- [ ] 5.4 Publish the frontend Release close behind the backend to minimize the admin-tool cutover gap; confirm the automated prod-pin bump + ArgoCD sync
- [ ] 5.5 Verify in prod directly: `List` returns published concerts grouped by artist in the console, `Delete` removes a test concert end-to-end (with cascade), and the approval queue (`ListPending`/`Approve`/`Reject`) still works under the renamed service; a non-admin token is still rejected at the admin host
