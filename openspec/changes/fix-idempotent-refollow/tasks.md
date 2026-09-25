## 1. Entity operation (components/entity/follow/follow)

- [ ] 1.1 In `FollowRepository.Follow`, inspect the `pgconn.CommandTag` returned by the `followInsertQuery` exec; when `RowsAffected() == 0` return `apperr.New(codes.AlreadyExists, "already following")` instead of `nil` (mirrors the `RowsAffected() == 0` check already used in `FollowRepository.SetHype`)
- [ ] 1.2 Add an integration test in `follow_repo_test.go` covering both spec scenarios: "First follow" (a fresh `Follow` call stores the row and returns no error) and "Repeat follow" (a second `Follow` call for the same user/artist returns `apperr.ErrAlreadyExists` and the original row, including its hype level, is unchanged); verify with `go test -tags=integration ./internal/infrastructure/database/rdb/... -run TestFollowRepository_Follow`

## 2. Usecase (components/usecase/follow/follow)

- [ ] 2.1 Confirm `internal/usecase/follow_uc_test.go`'s existing `TestFollowUseCase_Follow_PublishesAnalyticsEvent/does_not_publish_on_already-following_idempotent_path` subtest already covers the "Fan follows the same artist twice" scenario against a mocked repository (no usecase code change is required — `FollowUseCase.Follow` already treats `apperr.ErrAlreadyExists` from `Follow.Follow` as success without publishing); run `go test ./internal/usecase/... -run TestFollowUseCase_Follow` to verify it passes now that the mock's return value matches what the repository will actually return

## 3. Verification

- [ ] 3.1 Run `make lint` and `go test ./...` and confirm both pass
