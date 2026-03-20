## 1. Add `t.Parallel()` to usecase layer tests

- [x] 1.1 Add `t.Parallel()` to `artist_uc_test.go` (5 top-level tests + subtests)
- [x] 1.2 Add `t.Parallel()` to `concert_uc_test.go` (8 top-level tests + subtests)
- [x] 1.3 Add `t.Parallel()` to `concert_creation_uc_test.go` (top-level + subtests)
- [x] 1.4 Add `t.Parallel()` to `user_uc_test.go` (3 top-level tests + subtests)
- [x] 1.5 Add `t.Parallel()` to `entry_uc_test.go` (top-level + subtests)
- [x] 1.6 Add `t.Parallel()` to `artist_name_resolution_uc_test.go` (top-level + subtests)
- [x] 1.7 Add `t.Parallel()` to `push_notification_uc_test.go` (top-level + subtests)

## 2. Add `t.Parallel()` to adapter layer tests

- [x] 2.1 Add `t.Parallel()` to `adapter/rpc/artist_handler_test.go`
- [x] 2.2 Add `t.Parallel()` to `adapter/rpc/concert_handler_test.go`
- [x] 2.3 Add `t.Parallel()` to `adapter/rpc/entry_handler_test.go`
- [x] 2.4 Add `t.Parallel()` to `adapter/rpc/ticket_handler_test.go`
- [x] 2.5 Add `t.Parallel()` to `adapter/rpc/ticket_email_handler_test.go`
- [x] 2.6 Add `t.Parallel()` to `adapter/rpc/push_notification_handler_test.go`
- [x] 2.7 Add `t.Parallel()` to `adapter/rpc/health_handler_test.go`
- [x] 2.8 Add `t.Parallel()` to `adapter/rpc/mapper/artist_test.go`
- [x] 2.9 Add `t.Parallel()` to `adapter/event/artist_consumer_test.go`
- [x] 2.10 Add `t.Parallel()` to `adapter/event/concert_consumer_test.go`
- [x] 2.11 Add `t.Parallel()` to `adapter/event/artist_image_consumer_test.go`
- [x] 2.12 Add `t.Parallel()` to `adapter/event/notification_consumer_test.go`

## 3. Replace `time.After` with `synctest`

- [x] 3.1 Wrap `TestConcertUseCase_AsyncSearchNewConcerts` with `synctest.Test` and remove `time.After(5 * time.Second)` timeout
- [x] 3.2 Rewrite `receivePublishedConcerts` helper to use `synctest` instead of `time.After(200 * time.Millisecond)`
- [x] 3.3 Update `TestSearchNewConcerts_Deduplication` to work with synctest-compatible `receivePublishedConcerts`

## 4. Unify usecase test setup to deps-struct pattern

- [x] 4.1 Create `artistTestDeps` struct in `artist_uc_test.go` with `newArtistTestDeps(t)` constructor (matching `concertTestDeps` pattern)
- [x] 4.2 Refactor all test functions in `artist_uc_test.go` to use `artistTestDeps`
- [x] 4.3 Create `userTestDeps` struct in `user_uc_test.go` with `newUserTestDeps(t)` constructor
- [x] 4.4 Refactor all test functions in `user_uc_test.go` to use `userTestDeps`

## 5. Improve `cleanDatabase` signature

- [x] 5.1 Change `cleanDatabase()` to `cleanDatabase(t *testing.T)` in `setup_test.go`, add `t.Helper()`, replace `panic` with `t.Fatal`
- [x] 5.2 Update all callers in `artist_repo_test.go` to pass `t`
- [x] 5.3 Update all callers in `concert_repo_test.go` to pass `t`
- [x] 5.4 Update all callers in `user_repo_test.go` to pass `t`
- [x] 5.5 Update all callers in remaining rdb test files (`venue_repo_test.go`, `ticket_repo_test.go`, `ticket_email_repo_test.go`, `ticket_journey_repo_test.go`, `follow_repo_test.go`, `event_repo_test.go`, `nullifier_repo_test.go`, `search_log_repo_test.go`, `merkle_repo_test.go`, `push_subscription_repo_test.go`)

## 6. Implement ConcertHandler.List test

- [x] 6.1 Read `ConcertHandler.List` implementation to understand handler logic
- [x] 6.2 Replace placeholder test in `concert_handler_test.go` with meaningful assertions (request/response mapping, error cases)

## 7. Replace `assert.AnError` with specific errors in usecase tests

- [x] 7.1 Audit `concert_uc_test.go` for `assert.AnError` usage and replace with `apperr` errors where error type drives behavior
- [x] 7.2 Audit remaining usecase test files for `assert.AnError` and replace where applicable

## 8. Fix `logger, _ := logging.New()` error ignoring

- [x] 8.1 Create `newTestLogger(t)` helper in `usecase/helpers_test.go` (reusable across usecase tests)
- [x] 8.2 Replace all `logger, _ := logging.New()` in usecase test files with `newTestLogger(t)` call
- [x] 8.3 Replace all `logger, _ := logging.New()` in adapter/rpc test files with `newTestLogger(t)` or inline `require.NoError`

## 9. Verify

- [x] 9.1 Run `go test -race -count=3 ./internal/...` to verify parallel tests are race-free
- [x] 9.2 Run `make check` to ensure full CI compliance
