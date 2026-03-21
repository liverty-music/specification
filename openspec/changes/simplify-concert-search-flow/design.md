## Context

The discovery page currently uses a 5-layer call chain to determine when to show the Dashboard Coach Mark:

```
DiscoveryRoute → FollowOrchestrator → ConcertSearchTracker → ConcertServiceClient → RPC
```

`FollowOrchestrator` duplicates follow state that `FollowServiceClient` already manages. `ConcertSearchTracker` wraps polling logic that belongs in `ConcertServiceClient`. Both are page-scoped controllers that discard state on navigation — meaning Dashboard must re-fetch all concert data from scratch.

The project has established a state management pattern (see `state-management` spec): singleton services own `@observable` state, hydrate from localStorage, and persist via `propertyChanged` callbacks. `GuestService` and `OnboardingService` already follow this pattern. `FollowServiceClient` and `ConcertServiceClient` do not yet — they are stateless RPC wrappers.

## Goals / Non-Goals

**Goals:**

- Fix the Coach Mark bug: display when 3+ followed artists have concerts, regardless of how many artists are followed or still searching.
- Eliminate `FollowOrchestrator` and `ConcertSearchTracker` by absorbing their logic into singleton services.
- Make concert search state survive navigation (service-owned, not page-scoped).
- Reduce discovery page from 5 controllers to 3.

**Non-Goals:**

- Changing backend RPC APIs — this is frontend-only.
- Replacing polling with WebSocket/SSE — the polling mechanism itself works fine, the problem is where it lives and how completion is evaluated.
- Optimizing Dashboard loading with cached concert data — the service will hold the state, but Dashboard can adopt it incrementally.
- Persisting `artistsWithConcerts` to localStorage — this is session-scoped ephemeral state, not worth persisting.

## Decisions

### Decision 1: `FollowServiceClient` becomes the follow state SSoT

**Choice**: Add `@observable followedArtists: Artist[]` to `FollowServiceClient`. It hydrates from `GuestService.follows` (guest) or `listFollowed()` RPC (authenticated) and exposes `followedIds` / `followedCount` as derived getters.

**Why not keep FollowOrchestrator**: It holds a `followedArtists` array that is a copy of what the service already knows. The optimistic-update + rollback pattern belongs in the service (where the RPC call happens), not in a page-scoped controller. The `BubblePool.remove()` / `BubblePool.add()` calls for rollback are UI concerns that stay in `DiscoveryRoute`.

**Why not a new FollowStateService**: `FollowServiceClient` already has `follow()`, `unfollow()`, `listFollowed()` — adding state to it is natural, not a new abstraction.

### Decision 2: `ConcertServiceClient` owns polling and `artistsWithConcerts`

**Choice**: Add a `searchAndTrack(artistId)` method that encapsulates the full search lifecycle:

```
searchNewConcerts(artistId)     ← fire & forget to backend
startPolling()                  ← setInterval if not running
  pollSearchStatuses()          ← check pending artist statuses
    on completed → listConcerts(artistId)
      → has concerts → artistsWithConcerts.add(artistId)
      → artistsWithConcerts.size >= target → stopPolling (early exit)
    on timeout (15s) → mark done, skip listConcerts
```

**Why in the service, not a controller**: The polling is pure data-fetching logic with no UI dependencies. Moving it to the singleton service means: (a) state survives page navigation, (b) `DiscoveryRoute` becomes a thin event handler, (c) Dashboard or any future page can read `artistsWithConcerts`.

**Why `Set<string>` not `number`**: A Set prevents double-counting if `searchAndTrack` is called twice for the same artist (e.g., page reload with pre-seeded follows). The count is derived via `.size`.

### Decision 3: Per-artist concert check replaces batch verify

**Choice**: When a search status becomes `completed`, immediately call `listConcerts(artistId)` for that single artist. If concerts exist, add to `artistsWithConcerts` and emit a snack callback. Remove `verifyConcertsExist()` entirely.

**Why**: The current flow calls `verifyConcertsExist()` only after ALL searches complete, which is the root cause of the bug. Per-artist checking enables the "3 artists with concerts → Coach Mark" condition to trigger as soon as the third qualifying artist completes, regardless of others still pending.

**Alternative considered — count from `listSearchStatuses` response**: The RPC returns status only (pending/completed/failed), not whether concerts were found. A new RPC field would require backend changes, which is out of scope.

### Decision 4: Snack notification unified with search completion

**Choice**: The "artist has upcoming events" snack is emitted as a side effect of the per-artist `listConcerts` check inside `searchAndTrack`. The caller provides a callback for snack display. `checkLiveEvents()` in `FollowOrchestrator` is removed.

**Why**: Currently there are two separate `listConcerts` calls per artist — one in `checkLiveEvents` (immediate, optimistic) and one in `verifyConcertsExist` (deferred, batch). The new design makes exactly one `listConcerts` call per artist, at the right time (after backend search completes).

### Decision 5: Coach Mark condition simplified

**Choice**:

```typescript
get showDashboardCoachMark(): boolean {
  return this.isOnboarding
    && this.concertService.artistsWithConcertsCount >= TUTORIAL_FOLLOW_TARGET
}
```

**Why**: The condition no longer depends on `followedCount` at all. It answers only the question that matters: "have we found enough artists with concerts?" This is immune to the race condition where followedCount grows faster than searches complete.

### Decision 6: Polling lifecycle managed by AbortController

**Choice**: `ConcertServiceClient.searchAndTrack()` accepts an `AbortSignal`. When the discovery page detaches, it aborts the signal, which stops polling and cancels in-flight RPCs. The service clears its interval but retains `artistsWithConcerts` state.

**Why**: The service is a singleton that outlives the page. Polling must be tied to page lifecycle (no point polling after the user leaves discovery). But the accumulated state (`artistsWithConcerts`) should survive for Dashboard's benefit.

## Risks / Trade-offs

**[Risk] Service singleton holds polling state for a page-specific flow** → The polling is page-scoped via AbortSignal. The service only retains the result (`artistsWithConcerts`), not the polling mechanism. If the user returns to discovery, `searchAndTrack` re-checks and resumes polling for any new follows.

**[Risk] `listConcerts` called once per completed artist instead of batch** → Slightly more RPC calls than the current batch `verifyConcertsExist`. However, the calls are spread over time (as each artist completes) rather than concentrated, so actual load is smoother. And it eliminates the redundant `checkLiveEvents` call, so total RPC count may decrease.

**[Trade-off] Early polling stop at target count** → Once 3 artists with concerts are found, polling stops. Any remaining pending searches won't complete. This is acceptable because: (a) the Coach Mark goal is met, (b) the user is about to navigate to Dashboard which fetches fresh data via `listByFollower`, (c) the backend `SearchNewConcerts` fire-and-forget already ran — the data will be there for future requests regardless of frontend polling.
