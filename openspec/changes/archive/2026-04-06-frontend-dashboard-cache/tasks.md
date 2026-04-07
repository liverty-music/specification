## 1. ConcertServiceClient cache

- [x] 1.1 Add `cachedGroups: ProximityGroup[] | null`, `cacheTimestamp: number | null`, and `CACHE_TTL_MS = 24 * 60 * 60 * 1000` private fields to `ConcertServiceClient`
- [x] 1.2 Update `listByFollower()` to return `cachedGroups` on cache hit; store result and timestamp on cache miss
- [x] 1.3 Add public `invalidateFollowerCache()` method that sets both fields to `null`

## 2. FollowServiceClient integration

- [x] 2.1 Inject `IConcertService` into `FollowServiceClient`
- [x] 2.2 Call `concertService.invalidateFollowerCache()` in `follow()` after the follow RPC succeeds (inside the `try` block, after `await rpcClient.follow()`)
- [-] 2.3 ~~Skip `listFollowed()` RPC~~ — `followedArtists: Artist[]` does not store per-artist hype; skipping the RPC would lose hype data. Deferred: requires refactoring `followedArtists` to `FollowedArtist[]` first.

## 3. Tests

- [x] 3.1 Add unit test: `listByFollower()` returns cached value on second call without RPC
- [x] 3.2 Add unit test: `listByFollower()` re-fetches after cache expiry (mock `Date.now`)
- [x] 3.3 Add unit test: `follow()` calls `invalidateFollowerCache()` on success
- [x] 3.4 Add unit test: `follow()` does NOT call `invalidateFollowerCache()` on RPC failure
- [x] 3.5 Add unit test: `getFollowedArtistMap()` documents that `listFollowed()` RPC is always called (hype not in memory)
- [x] 3.6 Run `make check` and confirm all tests pass
