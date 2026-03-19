## Why

The `backend/internal/infrastructure/database/rdb` package has accumulated inconsistent test patterns, missing error case coverage for documented interface contracts, and underutilized test helpers. Two repository interfaces (`PushSubscriptionRepository`, `TicketJourneyRepository`) have zero test coverage, and several `ArtistRepository`/`FollowRepository` methods lack direct tests for their documented possible errors. These gaps reduce confidence in the repository layer and make future regressions harder to catch.

## What Changes

- **Standardize test patterns** across all `_test.go` files in the `rdb` package: consistent loop variable naming (`tt`), `args` struct style, `cleanDatabase()` placement (per-case via `setup`), and error assertion pattern (single `assert.ErrorIs` without redundant `require.Error`).
- **Add missing test files**: `push_subscription_repo_test.go`, `ticket_journey_repo_test.go`.
- **Add missing test cases** for documented possible errors: `ArtistRepository.Get`, `GetByMBID`, `List`, `CreateOfficialSite`, `GetOfficialSite`; `FollowRepository.Follow`, `Unfollow`, `SetHype`, `ListAll`, `ListFollowers`; `ConcertRepository.ListByArtist` (InvalidArgument); `VenueRepository.GetByPlaceID`; `SearchLogRepository.Delete`.
- **Eliminate `time.Sleep`** in `search_log_repo_test.go` (go-tester skill violation).
- **Refactor `search_log_repo_test.go`** from sequential subtests to table-driven tests.
- **Consolidate pointer helpers**: unify `strPtr()` and `ptr[T]()` into a single generic `ptr[T]` in `setup_test.go`.
- **Extract shared seed helpers**: `seedUser()`, `seedArtist()`, `seedVenue()` to replace duplicated raw SQL INSERT statements across test files.
- **Update `cleanTables()`** to include `push_subscriptions` table.

## Capabilities

### New Capabilities

(none -- this change is purely internal test quality improvement with no new user-facing capabilities)

### Modified Capabilities

(none -- no spec-level behavior changes, only test code)

## Impact

- **Code**: All `_test.go` files in `backend/internal/infrastructure/database/rdb/` and `setup_test.go`.
- **CI**: No changes to CI configuration. Test count will increase significantly.
- **Dependencies**: No new dependencies.
- **Risk**: Low. Changes are primarily confined to test files. One production bugfix was discovered during implementation: `push_subscription_repo.go`'s `ON CONFLICT DO UPDATE` clause used incorrect positional parameters (`$3`/`$4` mapped to `endpoint`/`p256dh` instead of `p256dh`/`auth`), causing upserts to write wrong values. Fixed by switching to `EXCLUDED.*` references.
