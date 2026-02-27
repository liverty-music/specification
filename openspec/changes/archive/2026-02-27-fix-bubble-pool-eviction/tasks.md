## 1. Proto (specification)

- [x] 1.1 Add `int32 limit` field to `ListSimilarRequest` (field 2, validation: gte=0, lte=100)
- [x] 1.2 Add `int32 limit` field to `ListTopRequest` (field 3, validation: gte=0, lte=100)
- [x] 1.3 Run `buf lint` and verify no breaking changes

## 2. Backend (Go)

- [x] 2.1 Update `ArtistSearcher` interface to accept `limit int32` in `ListSimilar` and `ListTop`
- [x] 2.2 Update Last.fm client to pass `limit` param when > 0 to `artist.getsimilar`, `geo.gettopartists`, `tag.gettopartists`, `chart.gettopartists`
- [x] 2.3 Update usecase layer to forward `limit` and include it in cache keys
- [x] 2.4 Add TODO placeholder in handler (`0` until proto is regenerated from BSR)
- [x] 2.5 Update all mocks and tests for new `limit` parameter signature

## 3. Frontend - ArtistDiscoveryService

- [x] 3.1 Add static constants `MAX_BUBBLES=50`, `SIMILAR_LIMIT_ON_TAP=30`, `MAX_SEED_ARTISTS=5`
- [x] 3.2 Remove `maxBubbles` instance property and `evictOldest()` method
- [x] 3.3 Rewrite `loadInitialArtists()` with following-count branching (Step 1-a / 1-b)
- [x] 3.4 Add `fetchSeedSimilarArtists()` and `pickRandomSeeds()` helpers for Step 1-b
- [x] 3.5 Add `dedup()` helper that filters by `isSeen()` and `isFollowed()`
- [x] 3.6 Modify `getSimilarArtists()` to accept `limit` param and NOT mutate `availableBubbles`
- [x] 3.7 Add `addToPool()` method that evicts oldest first, then inserts, using array reassignment
- [x] 3.8 Replace all `push()` / `splice()` calls with array reassignment for Aurelia observation
- [x] 3.9 Update `reloadWithTag()` to pass `limit` and use `dedup()`

## 4. Frontend - DnaOrbCanvas

- [x] 4.1 Update `handleInteraction()` to call `addToPool(similar)` instead of direct eviction + push
- [x] 4.2 Fade out evicted bubbles before spawning new ones

## 5. Testing

- [x] 5.1 Update `artist-discovery-service.spec.ts` for new API (remove `evictOldest`/`maxBubbles` tests, add `addToPool`/`getSimilarArtists` limit/dedup tests, add Step 1-a/1-b tests)
- [x] 5.2 Update `mock-rpc-clients.ts` to include `addToPool`, `isFollowed`, `searchArtists`, `reloadWithTag`
- [x] 5.3 Run full test suite and verify 269/269 pass
