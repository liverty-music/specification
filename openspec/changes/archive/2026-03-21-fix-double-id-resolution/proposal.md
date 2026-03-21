## Why

`FollowUseCase` already resolves external ID → internal UUID via `resolveUserID()` internally, but PR #246 added a second resolution in `FollowHandler` before calling the use case. The handler now passes `user.ID` (internal UUID) to the use case, which then calls `GetByExternalID(user.ID)` — searching the `external_id` column with a UUID string that was never stored there. This causes `not_found` on every authenticated follow-related RPC call.

## What Changes

- Remove `userRepo.GetByExternalID` calls from `FollowHandler` methods (`Follow`, `Unfollow`, `ListFollowed`, `SetHype`)
- Handler passes `claims.Sub` (external ID) directly to use case — the use case owns ID resolution
- Confirm `TicketJourneyUseCase` and `TicketEmailUseCase` do NOT have internal `resolveUserID` — handler-layer resolution is correct for those
- Update `FollowHandler` tests to reflect that `userRepo` is no longer injected into the handler

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `id-resolution`: Clarify that ID resolution responsibility belongs in the handler layer ONLY when the use case does not perform its own resolution internally. When the use case already resolves IDs (as `FollowUseCase` does), the handler must pass `claims.Sub` directly.

## Impact

- `backend/internal/adapter/rpc/follow_handler.go` — remove `userRepo` field and `GetByExternalID` calls
- `backend/internal/adapter/rpc/follow_handler_test.go` — remove `MockUserRepository` from handler tests
- `backend/internal/di/provider.go` — remove `userRepo` from `NewFollowHandler` call
- No proto changes, no DB migrations
