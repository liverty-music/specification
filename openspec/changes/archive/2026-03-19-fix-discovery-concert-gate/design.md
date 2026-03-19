## Context

The discovery page has two bugs caused by a mismatch between the onboarding step order and the implementation:

1. **Concert gate deadlock**: `verifyConcertData()` calls `listByFollower()`, which during onboarding delegates to `listWithProximity()`. This RPC requires `guest.home`, but home is set on the Dashboard (Step 3) — unreachable without passing the discovery gate (Step 1).
2. **Reload state loss**: `FollowOrchestrator.followedArtists` initializes as `[]` and is never hydrated from the persisted store. After reload, `followedIds` is empty, so `BubblePool.dedup()` cannot filter out followed artists.

The existing `ConcertService/List` RPC accepts only `artist_id` and returns concerts without auth or home. It is already used in `FollowOrchestrator.checkLiveEvents()`.

## Goals / Non-Goals

**Goals:**

- Break the circular dependency: discovery concert gate works without `guest.home`
- Restore followed state on reload so bubbles exclude followed artists
- Add test coverage for the discovery controllers that were untested

**Non-Goals:**

- Changing the onboarding step order (home selection stays on Dashboard)
- Adding a new backend RPC — reuse existing `ConcertService/List`
- Refactoring `ConcertServiceClient.listByFollower()` broadly — only change the verification path

## Decisions

### D1: Use `ConcertService/List` per-artist for concert existence check

**Decision**: Replace the single `listByFollower()` call in `ConcertSearchTracker.verifyConcertData()` with parallel `ConcertService/List` calls for each followed artist.

**Why**: `ConcertService/List` requires only `artist_id` — no auth, no home. It is already available in the frontend via `ConcertRpcClient.listConcerts()`.

**Alternatives considered**:
- *Add a new `ExistsConcerts` RPC*: Cleaner but requires proto change, BSR release cycle, and backend implementation for a gate that only fires once per session. Over-engineered for the use case.
- *Remove the concert gate entirely*: Simpler but degrades UX — users would reach the dashboard with an empty timetable if no concerts were found.

**Trade-off**: N+1 RPC calls (one per followed artist, typically 3–10). Acceptable because this runs once per session, the calls are parallel, and the response payloads are small.

### D2: Introduce a dedicated `verifyConcertsExist` method on `ConcertSearchClient` interface

**Decision**: Add a `verifyConcertsExist(artistIds: string[]): Promise<boolean>` method to the `ConcertSearchClient` interface used by `ConcertSearchTracker`. The implementation calls `ConcertService/List` per artist in parallel and returns `true` if any artist has ≥1 concert.

**Why**: Keeps `ConcertSearchTracker` decoupled from the specifics of which RPC is called. The tracker only needs to know "do concerts exist?" — the service layer decides how to answer.

### D3: Hydrate `FollowOrchestrator` from store in `DiscoveryRoute.loading()`

**Decision**: In `DiscoveryRoute.loading()`, read `store.getState().guest.follows` and pass the artist list to `FollowOrchestrator` before calling `loadInitialArtists()`.

**Why**: The store is already restored from localStorage by `loadPersistedState()` at app startup. The orchestrator just needs to be seeded from it. No new persistence mechanism required.

**Approach**: Add a `hydrate(artists: Artist[])` method on `FollowOrchestrator` that sets `followedArtists` from an external source. Call it at the top of `loading()`.

### D4: Unit tests for discovery controllers

**Decision**: Add Vitest unit tests for `ConcertSearchTracker`, `FollowOrchestrator`, and `BubbleManager`. These are plain classes (not DI-registered) that accept interfaces — easy to test with stubs.

**Why**: All three classes contain critical gate/filter logic with zero test coverage. The two bugs would have been caught by straightforward unit tests.

### D5: Fix E2E test to not pre-seed `guest.home`

**Decision**: Update the existing E2E coach mark test to remove `guest.home` from localStorage setup, validating that the coach mark works without home.

**Why**: The current test masks the bug by pre-seeding home. After fixing the implementation, the test should reflect the real user flow.

## Risks / Trade-offs

- **N+1 `List` calls**: 3–10 parallel RPCs per session. Mitigated by small payload size and one-time execution. If artist count grows, a batched RPC could be added later.
- **Race between hydrate and loadInitialArtists**: `hydrate()` must complete before `loadInitialArtists()` reads `followedIds`. Mitigated by calling them sequentially in `loading()` (synchronous hydrate, then async load).
- **`ConcertService/List` returns full concert objects**: We only need a boolean "exists". Acceptable overhead for now; a lightweight `Exists` RPC is a non-goal.
