## Why

Follow state on the Discovery page is split across two data structures: `BubblePool.followedIds` (Set) and `FollowOrchestrator.followedArtists` (Array), requiring manual synchronization on every follow/rollback. A recent controller-extraction refactoring consolidated the sync points into FollowOrchestrator, but the structural problem of maintaining two parallel data structures remains. This change removes follow-tracking responsibility from BubblePool and makes FollowOrchestrator the single source of truth, eliminating synchronization and improving testability.

## What Changes

- **BREAKING** Remove follow tracking from `BubblePool`: delete `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, `isFollowed()`
- **BREAKING** Change `BubblePool.dedup()` signature to `dedup(bubbles, followedIds: ReadonlySet<string>)` (inject followedIds externally)
- Make `FollowOrchestrator.followedArtists` the single source of truth for follow state; implement `followedIds` getter as a derived Set
- Inject `getFollowedIds` callback into `BubbleManager` and pass it to `pool.dedup()` calls
- No changes to `@aurelia/state` Store (no discovery slice added)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bubble-pool-lifecycle`: Remove follow-tracking responsibility from BubblePool; change `dedup` signature to accept external `followedIds`

## Impact

- `frontend/src/services/bubble-pool.ts` — Remove follow-related methods; change `dedup(bubbles, followedIds)` signature
- `frontend/src/routes/discovery/follow-orchestrator.ts` — Change `followedIds` getter from pool delegation to derived Set; replace `pool.markFollowed()` with `pool.remove()` + array update in `followArtist()`
- `frontend/src/routes/discovery/bubble-manager.ts` — Add `getFollowedIds` callback to constructor; pass followedIds to `pool.dedup()` calls
- `frontend/src/routes/discovery/discovery-route.ts` — Wire `() => this.follow.followedIds` into BubbleManager construction
- `frontend/src/routes/discovery/genre-filter-controller.ts` — Pass followedIds to `pool.dedup()` calls
- Update existing tests (BubblePool, FollowOrchestrator, BubbleManager, GenreFilterController)
