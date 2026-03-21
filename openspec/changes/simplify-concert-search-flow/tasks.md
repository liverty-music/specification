## 1. FollowServiceClient — SSoT for follow state

- [x] 1.1 Add `@observable followedArtists: Artist[]` to `FollowServiceClient` with `followedIds` and `followedCount` derived getters
- [x] 1.2 Add `hydrate(artists: Artist[])` method for onboarding page-load initialization from `GuestService.follows`
- [x] 1.3 Move optimistic update + rollback logic into `follow()` method (guest delegates to `GuestService`, authenticated calls RPC with rollback on failure)

## 2. ConcertServiceClient — polling and artistsWithConcerts state

- [x] 2.1 Add `artistsWithConcerts: Set<string>` and `artistsWithConcertsCount` getter to `ConcertServiceClient`
- [x] 2.2 Implement `searchAndTrack(artistId, signal, onConcertFound?)` — fire-and-forget `searchNewConcerts`, start polling, per-artist `listConcerts` on completion, add to set, early stop at target count
- [x] 2.3 Add per-artist timeout (15s) and AbortSignal support for polling lifecycle
- [x] 2.4 Remove `verifyConcertsExist()` method

## 3. DiscoveryRoute — simplify to thin event handler

- [x] 3.1 Replace `FollowOrchestrator` usage with direct `FollowServiceClient` calls + inline BubblePool UI operations (remove/add for rollback)
- [x] 3.2 Replace `ConcertSearchTracker` usage with `concertService.searchAndTrack()` calls, passing snack callback for `onConcertFound`
- [x] 3.3 Simplify `showDashboardCoachMark` to `isOnboarding && concertService.artistsWithConcertsCount >= TUTORIAL_FOLLOW_TARGET`
- [x] 3.4 Update `loading()` to hydrate follows into `FollowServiceClient` and call `searchAndTrack` for pre-seeded follows
- [x] 3.5 Update `BubbleManager` and `GenreFilterController` constructor references from `follow.followedIds` / `follow.followedArtists` to `followService` equivalents

## 4. Cleanup

- [x] 4.1 Delete `follow-orchestrator.ts`
- [x] 4.2 Delete `concert-search-tracker.ts`
- [x] 4.3 Remove `checkLiveEvents` call sites from `onArtistSelected` and `onFollowFromSearch`

## 5. Verification

- [x] 5.1 Run `make check` (lint + typecheck + unit tests) — passes (pre-existing TS error in user-client.ts unrelated to this change)
- [ ] 5.2 Manual E2E: follow 3+ artists on discovery page, verify Coach Mark appears when 3rd artist with concerts is found (not after all searches complete)
