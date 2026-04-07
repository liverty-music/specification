## Context

`DashboardRoute.loading()` calls three parallel RPCs on every navigation:
1. `FollowServiceClient.getFollowedArtistMap()` → internally calls `FollowRpcClient.listFollowed()`
2. `ConcertServiceClient.listByFollower()` → calls `ConcertRpcClient.listByFollower()`
3. `TicketJourneyService.listByUser()`

Concert data changes only on two events:
- Weekly cron job (dev: every Friday 09:00)
- First follow for an artist — which triggers `SearchNewConcerts()` **asynchronously** in a background goroutine; the follow RPC returns before the search completes

Both services are Aurelia DI singletons that persist across route navigations for the lifetime of the session. `FollowServiceClient` already maintains `@observable followedArtists` as authoritative in-memory state, updated optimistically on every follow/unfollow/setHype.

## Goals / Non-Goals

**Goals:**
- Eliminate redundant `listByFollower()` RPC calls on re-entry to Dashboard
- Eliminate redundant `listFollowed()` RPC calls when follow state is already in memory
- Invalidate `listByFollower()` cache when a follow action may have changed concert data
- Zero new runtime dependencies

**Non-Goals:**
- Caching `listByUser()` (ticket journeys — low visit frequency, complex invalidation)
- Service Worker / Cache Storage layer for RPC responses (POST responses cannot use Workbox CacheFirst; user-ID keying adds complexity)
- Redis or any shared cache (single backend replica; in-process MemoryCache already sufficient)
- Persistent cache across page reloads (session memory only)

## Decisions

### Decision 1: Cache location — ConcertServiceClient, not ConcertRpcClient

**Chosen**: cache in `ConcertServiceClient` (service layer)  
**Alternative**: cache in `ConcertRpcClient` (adapter layer)

The service layer has the semantic context needed to decide invalidation (e.g., "a follow happened"). The RPC client knows nothing about domain events. Placing the cache in the service layer also keeps it testable with Vitest without needing a mock transport.

### Decision 2: TTL = 24 hours

**Chosen**: 24-hour TTL as a safety backstop  
**Alternative**: infinite (session-scoped, invalidation-only)

The weekly cron job makes 24h a natural upper bound. Even if the invalidation on `follow()` is missed (e.g., network error before invalidation runs), the cache expires within 24h. This is conservative enough to avoid stale data in edge cases while still eliminating all intra-day re-fetches.

### Decision 3: Invalidate on follow(), not after SearchNewConcerts completes

**Chosen**: `invalidateFollowerCache()` called in `FollowServiceClient.follow()` after the follow RPC succeeds  
**Alternative**: poll/wait for `SearchNewConcerts` background goroutine to finish

`SearchNewConcerts` runs in a backend goroutine and has no notification mechanism. The follow RPC returns before it completes. Polling would add complexity and latency.

**Implication**: If the user navigates to Dashboard immediately after following an artist, the freshly invalidated cache will be repopulated but may not yet contain the new artist's concerts (the background search may still be running). This is acceptable: the data will appear on the next refresh or the next day's cron. A pull-to-refresh affordance addresses the impatient case.

### Decision 4: getFollowedArtistMap() continues to call listFollowed() on every navigation

**Chosen**: always call `listFollowed()` — optimization deferred  
**Originally planned**: skip the RPC when `this.followedArtists.length > 0`

During implementation it became clear that `followedArtists: Artist[]` stores only artist identity, not per-artist hype levels. `getFollowedArtistMap()` must return `Map<string, { artist, hype }>`, so skipping `listFollowed()` would silently drop all hype data from the dashboard rendering.

**Why deferred**: Fixing this requires refactoring `followedArtists` from `Artist[]` to `FollowedArtist[]` (which includes hype). That is a broader change touching optimistic updates in `follow()`, `unfollow()`, and hydration — out of scope for this change.

**Future opportunity**: Once `followedArtists` is refactored to carry hype, `getFollowedArtistMap()` can be updated to skip the RPC when the array is already populated.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| follow() RPC fails after invalidation | Invalidation only runs inside the `try` block after `await rpcClient.follow()` succeeds; on error the existing cache remains valid |
| `SearchNewConcerts` not done when user returns to Dashboard | Documented tradeoff; no mitigation needed beyond pull-to-refresh |
| Circular DI: FollowServiceClient → IConcertService | `ConcertServiceClient` does not import `IFollowServiceClient`; one-way dependency is safe |
| `followedArtists` stale on tab restore after long idle | Cache TTL (24h) covers this; on expiry the next `listByFollower()` call re-fetches |

## Migration Plan

No data migration. The cache is in-process only and starts empty on every session. Deploying the change requires no coordination with backend.

Rollback: revert the two frontend files; no state to clean up.

## Open Questions

- Should `unfollow()` also invalidate the concert cache? An unfollowed artist's concerts remain in the grouping until the cache expires. The TTL (24h) is acceptable for now; explicit invalidation on unfollow could be added later.
