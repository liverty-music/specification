## 1. Remove follow tracking from BubblePool

- [x] 1.1 Delete `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, `isFollowed()` from `BubblePool`
- [x] 1.2 Change `dedup()` signature to `dedup(bubbles: ArtistBubble[], followedIds: ReadonlySet<string>)`
- [x] 1.3 Remove `followedIds.clear()` from `reset()`

## 2. Make FollowOrchestrator the single source of truth

- [x] 2.1 Change `followedIds` getter from `pool.followedIds` delegation to `new Set(this.followedArtists.map(a => a.id))`
- [x] 2.2 Replace `pool.markFollowed(artist.id)` with `pool.remove(artist.id)` inside `followArtist()`
- [x] 2.3 Simplify rollback: remove `pool.unmarkFollowed()`, keep `pool.add([artist])` only (`followedArtists` filter unchanged)
- [x] 2.4 Change duplicate guard from `pool.isFollowed()` to `this.followedIds.has()`

## 3. Inject followedIds callback into BubbleManager

- [x] 3.1 Add `getFollowedIds: () => ReadonlySet<string>` parameter to constructor
- [x] 3.2 Change `pool.dedup(bubbles)` to `pool.dedup(bubbles, this.getFollowedIds())` in `loadInitialArtists()`
- [x] 3.3 Change `pool.dedup(rawBubbles)` to `pool.dedup(rawBubbles, this.getFollowedIds())` in `getSimilarArtists()`
- [x] 3.4 Change `pool.dedup(rawBubbles)` to `pool.dedup(rawBubbles, this.getFollowedIds())` in `loadReplacementBubbles()`
- [x] 3.5 Delete `followedIds` getter (BubbleManager no longer exposes follow state)

## 4. Update GenreFilterController dedup calls

- [x] 4.1 Change `pool.dedup(rawBubbles)` to `pool.dedup(rawBubbles, new Set(this.followedArtists().map(a => a.id)))` in `reloadWithTag()`

## 5. Update DiscoveryRoute wiring

- [x] 5.1 Pass `() => this.follow.followedIds` as the third argument to `BubbleManager` construction
- [x] 5.2 Verify `followedIds` getter delegates to `follow.followedIds` (FollowOrchestrator's derived getter)

## 6. Tests — BubblePool (`test/services/bubble-pool.spec.ts`)

- [x] 6.1 Delete `markFollowed / unmarkFollowed / isFollowed` describe block
- [x] 6.2 Remove `pool.markFollowed()` / `pool.isFollowed()` assertions from `reset` test
- [x] 6.3 Change `dedup > should filter out followed artists` to use `pool.dedup(bubbles, new Set(['a1']))` pattern
- [x] 6.4 Add test: `dedup(bubbles, emptySet)` works without follow filtering
- [x] 6.5 Add test: `dedup(bubbles, followedIds)` applies both seen and followed filters

## 7. Tests — FollowOrchestrator (`test/routes/discovery/follow-orchestrator.spec.ts`)

- [x] 7.1 Update existing `pool.isFollowed()` assertions to `sut.followedIds.has()`
- [x] 7.2 Add `followedIds derived getter` tests: empty → after follow → matches followedArtists
- [x] 7.3 Add `atomicity` test: after follow, IDs in followedIds are absent from pool
- [x] 7.4 Add `atomicity` test: after rollback, IDs absent from followedIds are restored in pool
- [x] 7.5 Add `regression: no dual-state desync` test: sequential follow (3) → rollback (1) → followedIds.size === 2 and only the rolled-back artist is restored to pool

## 8. Tests — BubbleManager (`test/routes/discovery/bubble-manager.spec.ts`)

- [x] 8.1 Update all `beforeEach` to pass `getFollowedIds` callback to `BubbleManager` constructor
- [x] 8.2 Delete `pool state sync > should expose followedIds through pool` test
- [x] 8.3 Add test: `loadInitialArtists` passes `getFollowedIds()` to pool.dedup
- [x] 8.4 Add test: `getFollowedIds` returns the latest value at call time (lazy evaluation verification)

## 9. Tests — GenreFilterController (`test/routes/discovery/genre-filter-controller.spec.ts`)

- [x] 9.1 Add test: followed artists returned by callback are excluded by dedup

## 10. Tests — Regression & final verification

- [x] 10.1 Grep confirms no remaining references to `pool.markFollowed` / `pool.unmarkFollowed` / `pool.isFollowed` / `pool.followedIds` across all test files
- [x] 10.2 `make check` passes (lint + test)
