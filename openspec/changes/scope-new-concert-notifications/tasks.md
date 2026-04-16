## 1. Specification (proto + release)

- [x] 1.1 Create a new branch off `origin/main` in the `specification` worktree
- [x] 1.2 Add `NotifyNewConcerts` RPC to `PushNotificationService` in `proto/liverty_music/rpc/push_notification/v1/push_notification_service.proto`
- [x] 1.3 Define `NotifyNewConcertsRequest` with `ArtistId artist_id` and `repeated EventId concert_ids`, with protovalidate constraints (`min_items = 1`, `max_items = 1000`) and full doc comments
- [x] 1.4 Define `NotifyNewConcertsResponse` (empty for now; reserved for future stats)
- [x] 1.5 Run `buf lint` and `buf format -w`
- [x] 1.6 Run `buf breaking --against '.git#branch=origin/main'` to confirm method addition is non-breaking
- [ ] 1.7 Open specification PR; wait for `buf-pr-checks.yml` and reviewer approval
- [ ] 1.8 After merge, cut a GitHub Release tag `vX.Y.Z` on specification → `buf-release.yml` pushes to BSR
- [ ] 1.9 Poll `gh run watch` until BSR generation workflow completes successfully

## 2. Backend — domain + event payload refactor

- [ ] 2.1 Create a new branch off `origin/main` in the `backend` worktree (can start in parallel with 1.x; use placeholder types for RPC stubs)
- [ ] 2.2 Introduce `internal/usecase/notification_events.go` (or equivalent) with exported `ConcertCreatedData` struct: fields `ArtistID string`, `ConcertIDs []string`, JSON tags `artist_id` and `concert_ids`
- [ ] 2.3 Remove `ConcertCreatedData` from `internal/entity/event_data.go`
- [ ] 2.4 Leave `SubjectConcertCreated` constant in `entity/event_data.go` (subject name is infrastructure naming, not payload shape)
- [ ] 2.5 Add `ConcertRepository.ListByIDs(ctx, ids []string) ([]*Concert, error)` to the interface in `internal/entity/concert.go`
- [ ] 2.6 Implement `ListByIDs` in `internal/infrastructure/database/rdb/concert_repo.go` using `WHERE event_id = ANY($1)` with pgx array binding; ensure venues are joined so `Concert.Venue.AdminArea` is populated
- [ ] 2.7 Update `internal/usecase/concert_creation_uc.go`: construct `ConcertCreatedData{ArtistID, ConcertIDs: ids}`, emit event only when `len(ConcertIDs) > 0`

## 3. Backend — use case + consumer refactor

- [ ] 3.1 Change `PushNotificationUseCase.NotifyNewConcerts` signature in `internal/usecase/push_notification_uc.go` to `NotifyNewConcerts(ctx context.Context, data ConcertCreatedData) error`
- [ ] 3.2 Inside the new implementation: resolve artist via `artistRepo.Get`, hydrate concerts via `concertRepo.ListByIDs`, then apply existing follower listing + hype filter + send loop unchanged
- [ ] 3.3 If `ListByIDs` returns zero rows, log at WARN and return nil
- [ ] 3.4 Slim `internal/adapter/event/notification_consumer.go`: parse CloudEvent into `usecase.ConcertCreatedData` and delegate; remove `artistRepo` and `concertRepo` fields and constructor parameters
- [ ] 3.5 Remove `artistRepo`/`concertRepo` wiring from `NotificationConsumer` construction in `internal/di/consumer.go`

## 4. Backend — debug RPC

- [ ] 4.1 Inject `config.ServerConfig` (or the relevant subset) into the push-notification RPC handler so `IsProduction()` is available at method entry — reuses the existing `ENVIRONMENT` env var, no new env var introduced
- [ ] 4.2 Implement `NotifyNewConcerts` handler method in `internal/adapter/rpc/push_notification_handler.go`:
  - If `cfg.IsProduction()` is true → return `connect.CodePermissionDenied`
  - Validate the request; resolve concerts via `concertRepo.ListByIDs` filtered by `artistID`; if any requested ID is missing from results → return `connect.CodeInvalidArgument`
  - Delegate to `PushNotificationUseCase.NotifyNewConcerts(ctx, ConcertCreatedData{ArtistID, ConcertIDs})`
  - Return empty response on success
- [ ] 4.3 Wire `NotifyNewConcerts` into the Connect handler registration in `internal/di/provider.go`
- [ ] 4.4 Ensure the existing auth interceptor continues to apply (JWT required for `UNAUTHENTICATED` path)
- [ ] 4.5 After BSR gen completes in task 1.9, run `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z` and `go mod tidy`
- [ ] 4.6 Swap any placeholder RPC types at TODO markers for generated types

## 5. Backend — tests

- [ ] 5.1 Update `internal/usecase/push_notification_uc_test.go` for the new signature; add a case asserting `venueAreas` is computed from the passed concerts only (home-filter regression test)
- [ ] 5.2 Update `internal/adapter/event/notification_consumer_test.go`: remove artist/concert repo mocks; assert the handler decodes the event and calls `pushNotificationUC.NotifyNewConcerts` with the expected struct
- [ ] 5.3 Update `internal/usecase/concert_creation_uc_test.go`: assert the published event payload carries `concert_ids` (exact IDs), not `concert_count`; assert event is suppressed when zero concerts are created
- [ ] 5.4 Add `internal/adapter/rpc/push_notification_handler_test.go` cases for `NotifyNewConcerts`:
  - `ENVIRONMENT=production` → returns `PermissionDenied`
  - unknown `concert_id` → returns `InvalidArgument`
  - happy path (`ENVIRONMENT=development`) → delegates to use case and returns empty response
- [ ] 5.5 Add an integration test that calls `NotifyNewConcerts` against a test DB and asserts `PushNotificationUseCase.NotifyNewConcerts` is invoked with the scoped concert set
- [ ] 5.6 Run `make check` locally and confirm all tests pass

## 6. Deploy + operate

- [ ] 6.1 Coordinate deploy order: backend PR merged → ArgoCD syncs; during the sync window purge the NATS `CONCERT` stream in dev (e.g., `nats stream purge CONCERT` from inside the cluster)
- [ ] 6.2 Verify consumer pod starts cleanly post-purge (no bad-payload CrashLoop)
- [ ] 6.3 Validate end-to-end by invoking `PushNotificationService.NotifyNewConcerts` via `grpcurl` or a small script against dev, using one of `pepperoni9+pixel@gmail.com`'s followed artists and a cherry-picked upcoming concert; confirm the push arrives on the Pixel
- [ ] 6.4 Repeat the NATS purge + validation in staging

## 7. Documentation

- [ ] 7.1 Add a short runbook note to `backend/docs/` describing the debug RPC (purpose, production gate, example invocation)
- [ ] 7.2 Archive this change via `/opsx:archive` after PRs are merged and validation passes
