## Why

Following an artist a fan already follows is not a no-op: `followInsertQuery` uses `ON CONFLICT DO NOTHING`, so a duplicate follow returns no error, and `FollowUseCase.Follow` can only detect "already following" by treating an `AlreadyExists` error from `Follow.Follow` as success. Since the repository never returns that error, every repeat follow tap is treated as a brand-new follow: it re-publishes `ARTIST.followed` (inflating the `artist.follow.completed` analytics funnel) and re-runs the official-site-resolution and first-concert-search background work. The `components/entity/follow/follow` spec currently documents the opposite of the fix — it states Follow "SHALL never fail with AlreadyExists" — while the Go interface doc comment and the usecase spec already assume the AlreadyExists contract; the entity spec needs to change to match.

## What Changes

- `Follow.Follow` SHALL fail with `AlreadyExists` when the fan already follows the artist, instead of silently succeeding. The row itself, and its hype level, are left untouched.
- `FollowUseCase.Follow` continues to treat `AlreadyExists` from `Follow.Follow` as success (already implemented and already spec'd); this change removes the "Known defect" annotation on that requirement now that the entity layer will actually produce the error it depends on.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `components/entity/follow/follow`: Follow SHALL fail with AlreadyExists on a duplicate follow (reversing the current "SHALL never fail with AlreadyExists" requirement, which described the buggy ON CONFLICT DO NOTHING behavior).
- `components/usecase/follow/follow`: no requirement text changes (the "repeat follow changes nothing" behavior is already correctly spec'd); only the "Known defect: liverty-music/backend#473" annotation is removed now that the entity-layer contract it depends on is fixed.

## Impact

- **Backend**: `internal/infrastructure/database/rdb/follow_repo.go` (`FollowRepository.Follow` reports `RowsAffected == 0` as `AlreadyExists`), `internal/infrastructure/database/rdb/follow_repo_test.go` (integration test for the duplicate-insert path), `internal/usecase/follow_uc_test.go` (already covers the idempotent path via a mocked repo; no change needed).
- **No proto/RPC changes**: the RPC-facing behavior (`Follow` always succeeds for the caller) is unchanged; only the internal repository-to-usecase contract is corrected.
