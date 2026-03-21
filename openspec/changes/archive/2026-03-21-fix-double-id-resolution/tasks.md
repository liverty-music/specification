## 1. Revert FollowHandler to pass claims.Sub to use case

- [x] 1.1 Remove `userRepo entity.UserRepository` field from `FollowHandler` struct
- [x] 1.2 Remove `userRepo entity.UserRepository` parameter from `NewFollowHandler`
- [x] 1.3 In `Follow`: replace `userRepo.GetByExternalID` + `user.ID` with `claims.Sub` passed directly to use case
- [x] 1.4 In `Unfollow`: same — pass `claims.Sub` directly to use case
- [x] 1.5 In `ListFollowed`: same — pass `claims.Sub` directly to use case
- [x] 1.6 In `SetHype`: same — pass `claims.Sub` directly to use case
- [x] 1.7 Remove unused `entity` import from `follow_handler.go` if no longer needed

## 2. Update DI wiring

- [x] 2.1 Remove `userRepo` argument from `NewFollowHandler(...)` call in `di/provider.go`

## 3. Update tests

- [x] 3.1 Remove `entitymocks.MockUserRepository` from `follow_handler_test.go` (handler no longer holds userRepo)
- [x] 3.2 Update `TestFollowHandler_Follow` success case: mock expects `uc.Follow(ctx, "ext-user-1", artistID)` (external ID, not UUID)
- [x] 3.3 Update `TestFollowHandler_Unfollow` success case: mock expects `uc.Unfollow(ctx, "ext-user-1", artistID)`
- [x] 3.4 Update `TestFollowHandler_ListFollowed` success case: mock expects `uc.ListFollowed(ctx, "ext-user-1")`
- [x] 3.5 Update `TestFollowHandler_SetHype` success case: mock expects `uc.SetHype(ctx, "ext-user-1", artistID, ...)`
- [x] 3.6 Remove "user not found" test cases from FollowHandler tests (handler no longer calls GetByExternalID)
- [x] 3.7 Remove `followAuthedCtx` helper if it duplicates the ticket-journey helper (or keep for clarity)

## 4. Verify and deploy

- [x] 4.1 Run `make check` in backend repo
- [ ] 4.2 Confirm `FollowService/ListFollowed` returns 200 after deploy
