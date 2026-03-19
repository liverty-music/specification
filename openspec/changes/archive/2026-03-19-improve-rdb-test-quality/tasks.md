## 1. Foundation: setup_test.go improvements

- [x] 1.1 Add generic `ptr[T any](v T) *T` helper to `setup_test.go`
- [x] 1.2 Add shared seed helpers: `seedUser(t, name, email, externalID) string`, `seedArtist(t, name, mbid) string`, `seedVenue(t, name) string`, `seedEvent(t, venueID, artistID, title, date) string`
- [x] 1.3 Add `push_subscriptions` to `cleanTables()` table list (before `users` for FK order)
- [x] 1.4 Remove `strPtr()` from `venue_repo_test.go` (replaced by generic `ptr`)

## 2. Normalize existing test files (pattern consistency)

- [x] 2.1 `ticket_repo_test.go`: Rename loop variable `tc` → `tt`; remove redundant `require.Error` before `assert.ErrorIs`; replace `seedTicketTestData` internals with shared seed helpers
- [x] 2.2 `venue_repo_test.go`: Replace anonymous `args` struct with named `type args struct`; replace `strPtr` calls with `ptr`
- [x] 2.3 `search_log_repo_test.go`: Remove `time.Sleep`; refactor `Upsert`/`UpdateStatus` from sequential subtests to table-driven with per-case `cleanDatabase()` in `setup`
- [x] 2.4 `follow_repo_test.go`: Replace raw SQL user INSERT with `seedUser`; remove vestigial `args` struct assignment in loop body
- [x] 2.5 `nullifier_repo_test.go`: Replace raw SQL event/venue/artist INSERT in subtests with shared seed helpers
- [x] 2.6 `concert_repo_test.go`: Skipped — fixtures use specific IDs and coordinates tightly coupled to assertions
- [x] 2.7 `ticket_email_repo_test.go`: Skipped — `seedTicketEmailTestData` already uses helper-like pattern; `ptr[T]` moved to setup_test.go

## 3. Add missing test cases for existing repositories

- [x] 3.1 `artist_repo_test.go`: Add `TestArtistRepository_Get` (success + NotFound)
- [x] 3.2 `artist_repo_test.go`: Add `TestArtistRepository_GetByMBID` (success + NotFound)
- [x] 3.3 `artist_repo_test.go`: Add `TestArtistRepository_List` (empty + multiple artists)
- [x] 3.4 `artist_repo_test.go`: Add `TestArtistRepository_CreateOfficialSite` (success + AlreadyExists)
- [x] 3.5 `artist_repo_test.go`: Add `TestArtistRepository_GetOfficialSite` (success + NotFound)
- [x] 3.6 `follow_repo_test.go`: Add `TestFollowRepository_Follow` (success + idempotent duplicate)
- [x] 3.7 `follow_repo_test.go`: Add `TestFollowRepository_Unfollow` (success + idempotent non-existent)
- [x] 3.8 `follow_repo_test.go`: Add `TestFollowRepository_SetHype` (success + NotFound)
- [x] 3.9 `follow_repo_test.go`: Add `TestFollowRepository_ListAll` (empty + with followed artists)
- [x] 3.10 `follow_repo_test.go`: Add `TestFollowRepository_ListFollowers` (empty + with followers + includes Home data)
- [x] 3.11 `concert_repo_test.go`: Skipped — ListByArtist doesn't validate empty ID (returns empty slice, not error)
- [x] 3.12 `venue_repo_test.go`: Add `TestVenueRepository_GetByPlaceID` (success + NotFound)
- [x] 3.13 `search_log_repo_test.go`: Add `TestSearchLogRepository_Delete` (success + idempotent delete)

## 4. New test files for untested repositories

- [x] 4.1 Create `push_subscription_repo_test.go`: `TestPushSubscriptionRepository_Create` (new + upsert on same endpoint)
- [x] 4.2 `push_subscription_repo_test.go`: `TestPushSubscriptionRepository_DeleteByEndpoint` (existing + non-existent idempotent)
- [x] 4.3 `push_subscription_repo_test.go`: `TestPushSubscriptionRepository_ListByUserIDs` (empty input + matching + no matches)
- [x] 4.4 `push_subscription_repo_test.go`: `TestPushSubscriptionRepository_DeleteByUserID` (with subscriptions + idempotent)
- [x] 4.5 Create `ticket_journey_repo_test.go`: `TestTicketJourneyRepository_Upsert` (create + update status)
- [x] 4.6 `ticket_journey_repo_test.go`: `TestTicketJourneyRepository_Delete` (existing + idempotent non-existent)
- [x] 4.7 `ticket_journey_repo_test.go`: `TestTicketJourneyRepository_ListByUser` (empty + multiple journeys)

## 5. Verification

- [x] 5.1 Run `make test` to confirm all tests pass
- [x] 5.2 Run `make check` to confirm lint + tests pass
