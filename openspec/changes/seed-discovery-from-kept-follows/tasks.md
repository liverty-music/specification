# Tasks

All tasks are in the frontend repository. Each test carries `@spec components/infrastructure/fan/web/route/discovery "<scenario>"` for the scenarios it covers.

## 1. Kept follows (design D1)

- [x] 1.1 Add `src/adapter/storage/followed-artists-storage.ts` (save, load per `sub`, clear) and keep the signed-in list in `FollowStore.listFollowed`; clear it on `SignedOut`; expose `keptFollowedArtists()`. Verify `src/services/follow-store.spec.ts` covers the per-account read and the sign-out clear

## 2. Seeds from the kept list (design D2)

- [x] 2.1 `ArtistBubbleStore.prefetchInitial(viewportWidth, seedsFrom)` picks seeds from `seedsFrom` and still excludes the current follow list; `runDiscoveryPrefetch` passes the kept list without awaiting the follow list, and awaits it when nothing is kept. Verify the unit tests in `artist-bubble-store.spec.ts` and `discovery-prefetch-task.spec.ts`

## 3. Release and measure

- [ ] 3.1 Release, then measure about 10 signed-in loads on the reference setup and record the medians under "Measurements" in design.md
