## Why

Every route navigation to Dashboard fires three parallel RPCs unconditionally, even when the underlying data cannot have changed (concerts update only on the weekly cron job or on a first-follow event). This produces unnecessary backend load and noticeably slow dashboard loads on re-entry. Adding a targeted in-memory cache with event-driven invalidation eliminates redundant network round-trips at zero infrastructure cost.

## What Changes

- `ConcertServiceClient.listByFollower()` gains a 24-hour in-memory cache keyed per authenticated user session; the cache is invalidated on `follow()`.
- ~~`FollowServiceClient.getFollowedArtistMap()` skips the `listFollowed()` RPC when `followedArtists` is already populated in memory (the service already tracks this state via `@observable`).~~ *(deferred — see design Decision 4; `listFollowed()` is called on every invocation to provide hype data)*
- `FollowServiceClient.follow()` calls `concertService.invalidateFollowerCache()` after a successful follow RPC to ensure the next dashboard load reflects newly discovered concerts.

## Capabilities

### New Capabilities

- `dashboard-concert-cache`: In-memory cache for `listByFollower()` RPC results in the frontend, with event-driven invalidation on follow actions.

### Modified Capabilities

<!-- No existing spec-level requirements are changing. The caching is an internal
     implementation detail of the service layer; no public API contract or
     existing capability spec changes. -->

## Impact

- **Frontend**: `src/services/concert-service.ts`, `src/services/follow-service-client.ts`
- **No backend changes**: cache lives entirely in the Aurelia singleton service layer
- **No new dependencies**: uses native `Date.now()` for TTL; no external cache library
- **No SW changes**: Connect-RPC uses HTTP POST; Workbox CacheFirst strategies do not apply
