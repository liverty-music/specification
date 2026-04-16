## 1. Specification (proto + release)

- [x] 1.1 Create a new branch off `origin/main` in the `specification` worktree
- [x] 1.2 Add `NotifyNewConcerts` RPC to `PushNotificationService` in `proto/liverty_music/rpc/push_notification/v1/push_notification_service.proto`
- [x] 1.3 Define `NotifyNewConcertsRequest` with `ArtistId artist_id` and `repeated EventId concert_ids`, with protovalidate constraints (`min_items = 1`, `max_items = 1000`) and full doc comments
- [x] 1.4 Define `NotifyNewConcertsResponse` (empty for now; reserved for future stats)
- [x] 1.5 Run `buf lint` and `buf format -w`
- [x] 1.6 Run `buf breaking --against '.git#branch=origin/main'` to confirm method addition is non-breaking
- [x] 1.7 Open specification PR liverty-music/specification#407; merged 2026-04-16T06:24Z
- [x] 1.8 Cut GitHub Release v0.37.0 → `buf-release.yml` triggered
- [x] 1.9 BSR gen completed successfully (run 24495543550)

## 2. Backend — domain + event payload refactor

- [x] 2.1 Create a new branch `279-scope-new-concert-notifications` off `origin/main` in the `backend` worktree (liverty-music/backend#279)
- [x] 2.2 Introduce `internal/usecase/notification_events.go` with exported `ConcertCreatedData` struct
- [x] 2.3 Remove `ConcertCreatedData` from `internal/entity/event_data.go`
- [x] 2.4 Leave `SubjectConcertCreated` constant in `entity/event_data.go`
- [x] 2.5 Add `ConcertRepository.ListByIDs(ctx, ids []string) ([]*Concert, error)` to the interface
- [x] 2.6 Implement `ListByIDs` in `concert_repo.go` with `WHERE event_id = ANY($1)` and venue join
- [x] 2.7 Update `concert_creation_uc.go`: emit `ConcertCreatedData{ArtistID, ConcertIDs}`, skip when 0

## 3. Backend — use case + consumer refactor

- [x] 3.1 Change `PushNotificationUseCase.NotifyNewConcerts` signature to `(ctx, data ConcertCreatedData) error`
- [x] 3.2 Inside implementation: resolve artist + concerts via repos, then existing hype filter + send loop
- [x] 3.3 If `ListByIDs` returns zero rows, log at WARN and return nil
- [x] 3.4 Slim `notification_consumer.go`: parse CloudEvent → delegate; removed repo fields
- [x] 3.5 Remove repo wiring from `NotificationConsumer` in `consumer.go` + updated `provider.go` to pass repos to use case

## 4. Backend — debug RPC

- [x] 4.1 Inject `config.BaseConfig` + `concertRepo` into the push-notification RPC handler; `isProduction` cached at construction
- [x] 4.2 Implement `NotifyNewConcerts` handler: IsProduction → PermissionDenied; validate; ListByIDs + ownership check; delegate
- [x] 4.3 Wire updated handler into `internal/di/provider.go`
- [x] 4.4 JWT auth enforced via `mapper.GetExternalUserID(ctx)` inside the method (UNAUTHENTICATED path)
- [x] 4.5 Upgraded generated packages: protobuf v1.36.11-20260416062534, connectrpc v1.19.1-20260416062534; `go mod tidy` ran
- [x] 4.6 Stale BSR TODO comment removed from handler imports

## 5. Backend — tests

- [x] 5.1 Update `push_notification_uc_test.go` for new signature + HOME-filter regression test
- [x] 5.2 Update `notification_consumer_test.go`: removed repo mocks; assert delegation to UC
- [x] 5.3 Update `concert_creation_uc_test.go`: assert `concert_ids` payload; assert no publish on 0
- [x] 5.4 Add `push_notification_handler_test.go` NotifyNewConcerts cases (PermissionDenied / Unauthenticated / InvalidArgument / happy path)
- [ ] ~~5.5 Integration test (deferred: local Postgres port 5432 conflict with devcontainer; covered by unit tests + dev-env validation in task 6.3)~~
- [x] 5.6 Unit test suite + `make lint` pass locally

## 6. Deploy + operate

- [x] 6.1 Backend merged (PR #280) → Deploy Backend workflow success → ArgoCD rolled out server-app + consumer-app; purged NATS CONCERT stream (40 messages) via `kubectl port-forward` + `nats stream purge CONCERT`
- [x] 6.2 Consumer pod (consumer-app-bc4b8d964-qnpjj) started cleanly post-purge; all 6 handlers subscribed, no CrashLoop
- [x] 6.3 End-to-end smoke test passed: NotifyNewConcerts RPC returned HTTP 200 in 290ms; pipeline executed correctly (artist hydrated, concerts fetched by ID, hype filter applied, 2 subscriptions fan-out attempted). Webpush delivery returned 403 (separate VAPID config issue, pre-existing, out of scope for this change — to be tracked as new issue)
- [ ] ~~6.4 Staging purge + validation — deferred: blocked by VAPID issue (separate ticket); will be reattempted alongside the VAPID fix~~

## 7. Documentation

- [x] 7.1 Add runbook at `backend/docs/debug-rpc-notify-new-concerts.md`
- [x] 7.2 Archive this change via `/opsx:archive` after PRs are merged and validation passes
