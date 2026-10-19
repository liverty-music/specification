## Context

`runDiscoveryPrefetch` (frontend `src/services/discovery-prefetch-task.ts`) starts the initial load during start-up for an app opened on Discovery: for a signed-in fan it awaits `FollowStore.ensureLoaded()`, then `ArtistBubbleStore.prefetchInitial`, which picks up to 5 seeds from the follow list and sends one `ListSimilar` per seed. Long-animation-frame measurements on the reference setup (clean Chrome, owner's account, v1.108.2, 3 loads) show the main thread busy from about 0.6 s to 3.6–4.4 s: `main.js` evaluation (800–940 ms), the start-up after `config.json` (430–600 ms), the app shell (500–800 ms) and the Discovery route's first render (440–530 ms). The follow-list response (about 2.6 s) is handled after them, and `ListSimilar` follows 100–200 ms later.

## Goals / Non-Goals

- Goal: send the signed-in seeds during start-up, not after the follow list.
- Non-goal: shorten start-up itself (route chunks load eagerly until the Aurelia 2.1 upgrade).
- Non-goal: keep or redraw the bubble field across starts (declined in `speed-up-discovery-bubble-reveal` D13).

## Decisions

### 1. Keep the follow list's identity fields per account

`FollowStore.listFollowed` saves `{ sub, artists: [{ id, name, mbid }] }` under `follow.keptArtists` after each signed-in load, through `src/adapter/storage/followed-artists-storage.ts`; `SignedOut` removes it. `keptFollowedArtists()` returns the list only for the signed-in `sub`, so another account on the same browser never seeds from it. Only identity is kept: the list is a hint for seeds, not the follow state, which stays `followedArtists`.

### 2. Seeds from the kept list; exclusion from the current list

`prefetchInitial(viewportWidth, seedsFrom)` passes the kept list to the initial load, which uses it to pick seeds and to reset the seen-tracker. The field is still set through `freshFrom` / `setField`, which exclude `FollowStore.followedIds` at that moment; by then this session's list has normally arrived (it answers before the similar requests). A kept artist the fan has unfollowed since can still be a seed: its similar artists are a fair suggestion and it is itself excluded as seen. When there is no kept list the start-up load waits for the follow list as before.

Rejected: hydrating `FollowStore.followedArtists` from the kept list. Every screen and the optimistic follow/unfollow paths read that projection, so a stale list would show in My Artists and could fight the follow writes.

## Risks / Trade-offs

- An artist followed on another device since the kept list can appear as a bubble if the field is set before this session's list answers. The route's re-entry delta (`reenter`) removes it on the next visit; the case needs a follow elsewhere and a slow follow list.
- One more key in localStorage, a few KB for a large follow list.

## Measurements

To be recorded after release: about 10 signed-in repeat-visit loads on the reference setup, `ghosts_ms` and `first_name_ms` medians, against v1.107.0's 2,996 / 5,008 ms.
