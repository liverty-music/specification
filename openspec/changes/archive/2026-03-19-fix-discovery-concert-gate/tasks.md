## 1. Fix concert data gate (remove home dependency)

- [x] 1.1 Add `verifyConcertsExist(artistIds: string[]): Promise<boolean>` to `ConcertSearchClient` interface in `concert-search-tracker.ts`
- [x] 1.2 Implement `verifyConcertsExist` in `ConcertServiceClient` (`concert-service.ts`): call `ConcertService/List` per artist in parallel, return `true` if any has ≥1 concert
- [x] 1.3 Replace `listByFollower()` call in `ConcertSearchTracker.verifyConcertData()` with `verifyConcertsExist()` and set `concertGroupCount` based on the boolean result

## 2. Hydrate follow state on reload

- [x] 2.1 Add `hydrate(artists: Artist[]): void` method to `FollowOrchestrator` that sets `followedArtists` from external source
- [x] 2.2 In `DiscoveryRoute.loading()`, read `store.getState().guest.follows` during onboarding and call `follow.hydrate()` before `loadInitialArtists()`

## 3. Unit tests

- [x] 3.1 Create `concert-search-tracker.spec.ts`: test `verifyConcertData` calls `verifyConcertsExist` (no home needed), test gate with 0 concerts returns false, test gate with ≥1 concert returns true, test `syncPreSeeded` starts polling for pre-seeded artists
- [x] 3.2 Create `follow-orchestrator.spec.ts`: test `hydrate` populates `followedIds`, test `followArtist` adds to `followedIds`, test optimistic rollback restores state
- [x] 3.3 Create `bubble-manager.spec.ts`: test `loadInitialArtists` excludes followed artists via `followedIds`, test with pre-hydrated follows filters correctly

## 4. E2E tests

- [x] 4.1 Update `onboarding-flow.spec.ts` "Spotlight is visible" test: remove `guest.home` from localStorage setup, verify coach mark appears without home
- [x] 4.2 Add E2E test: discovery page reload with pre-seeded follows — verify followed artists do not appear as bubbles
