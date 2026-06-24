## 1. Concert-discovery notification: surface recipient language

- [x] 1.1 Extend `followListFollowersQuery` in `internal/infrastructure/database/rdb/follow_repo.go` to select `COALESCE(u.preferred_language, '')`
- [x] 1.2 Scan the new column in `ListFollowers` and set `Follower.User.PreferredLanguage`; update the `ListFollowers` doc comment and the `FollowRepository.ListFollowers` interface doc in `internal/entity/follow.go`
- [x] 1.3 Add/extend an integration test in `internal/infrastructure/database/rdb/follow_repo_test.go` asserting `ListFollowers` returns `preferred_language` (set via UPDATE) and empty string when unset

## 2. Concert-discovery notification: localized payload

- [x] 2.1 Change `NewConcertNotificationPayload` in `internal/entity/push_notification.go` to accept a `lang` parameter, normalize empty/unsupported → `en`, and render an en/ja body with singular/plural handling ("1 new concert found" / "N new concerts found" / "新しいライブが N 件見つかりました")
- [x] 2.2 Add table-driven unit tests in `internal/entity/push_notification_test.go` covering en, ja, empty-lang fallback, and singular vs plural
- [x] 2.3 In `NotifyNewConcerts` (`internal/usecase/push_notification_uc.go`), build a `map[userID]lang` during follower filtering and a `map[lang][]byte` payload cache, marshalling at most once per distinct language; send the per-language payload to each subscription (default `en` when a sub's user is absent), leaving 410-gone cleanup, metrics, and error handling unchanged
- [x] 2.4 Extend `internal/usecase/push_notification_uc_test.go` to assert ja vs en bodies from captured payload bytes for a mixed-language audience, plus empty-lang → en fallback

## 3. Sales-phase announcement: per-recipient localization

- [x] 3.1 Add `userRepo entity.UserRepository` to the struct and constructor of `internal/usecase/sales_phase_announcement_uc.go`
- [x] 3.2 In `AnnounceDiscoveredPhase`, hydrate recipients via `userRepo.Get` (warn-and-skip on error, mirroring `sales_reminder_uc.go`) and build a `map[userID]lang`
- [x] 3.3 Replace the hardcoded English payload with `announcementTitle(lang)` / `announcementBody(lang)` helpers (map + en fallback) and a `map[lang][]byte` cache; remove the "personalisation intentionally omitted" comment
- [x] 3.4 Wire `rdb.NewUserRepository(db)` into the announcement use case in `internal/di/consumer.go`
- [x] 3.5 Add `internal/usecase/sales_phase_announcement_uc_test.go` covering en, ja, empty-lang → en, `userRepo.Get` error → skip-but-continue, and empty-audience no-op

## 4. Verification and release

- [x] 4.1 Run `make check` (lint + unit + integration tests) in `backend` until green
- [x] 4.2 Open the backend PR, get CI green, and merge
- [x] 4.3 Cut a backend release (SemVer tag + GitHub Release) and confirm the prod image is built
- [x] 4.4 Confirm the prod rollout (ArgoCD synced/healthy) so concert-discovery and sales-phase-announcement notifications ship to prod recipients in their preferred language
