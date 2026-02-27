## Why

When a user taps an artist bubble on the /discover or /onboarding/discover page, all bubbles disappear instead of just the tapped one. The root cause is that `getSimilarArtists()` pushes new artists into the `availableBubbles` array before the overflow calculation in `handleInteraction()`, causing `evictOldest()` to remove nearly all existing bubbles. This makes the discovery experience unusable after the first tap.

## What Changes

- **Fix bubble eviction ordering**: Evict oldest bubbles *before* adding similar artists to the pool, not after.
- **Redesign initial load branching**: When the user already follows artists, seed the bubble pool from `ListSimilar` of random followed artists instead of `ListTop`.
- **Add `limit` parameter to `ListSimilar` and `ListTop` RPCs**: Allow the frontend to control how many results are returned per call.
- **Introduce `addToPool()` method**: Replace direct array mutation with a single method that handles eviction + insertion atomically, using array reassignment for Aurelia 2 reactivity.
- **Remove `evictOldest()` and `maxBubbles` instance property**: Replace with `addToPool()` and `MAX_BUBBLES` static constant.

## Capabilities

### New Capabilities

- `bubble-pool-lifecycle`: Defines the bubble pool initialization, eviction, deduplication, and tap-to-refill lifecycle for the artist discovery UI.

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: The "Similar artist bubble spawning" scenario changes — `getSimilarArtists()` no longer pushes into the pool directly; the caller manages eviction and insertion via `addToPool()`. Initial load now branches based on followed-artist count.

## Impact

- **specification** (proto): `ListSimilarRequest` and `ListTopRequest` gain an `int32 limit` field.
- **backend** (Go): `ArtistSearcher` interface, Last.fm client, and usecase layer accept and forward the `limit` parameter.
- **frontend** (Aurelia 2): `ArtistDiscoveryService` rewritten — `loadInitialArtists()` branches on followed count, `getSimilarArtists()` becomes a pure fetch (no pool mutation), new `addToPool()` method handles capped insertion. `DnaOrbCanvas.handleInteraction()` updated to use the new API. All array mutations replaced with reassignment for Aurelia observation.
