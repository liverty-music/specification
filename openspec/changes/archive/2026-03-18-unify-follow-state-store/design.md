## Context

A recent refactoring (2026-03-17) split DiscoveryRoute into five controllers:

- `FollowOrchestrator` — follow/unfollow/rollback
- `BubbleManager` — pool and physics coordination
- `GenreFilterController` — genre filtering
- `SearchController` — artist search
- `ConcertSearchTracker` — concert search tracking

This split consolidated follow logic into FollowOrchestrator, but follow state still lives in two places:

1. `BubblePool.followedIds` (Set) — used by dedup and template bindings
2. `FollowOrchestrator.followedArtists` (Array) — used for the followed artist list and count

Inside `followArtist()`, `pool.markFollowed()` and `followedArtists = [...]` must be manually kept in sync.

## Goals / Non-Goals

**Goals:**

- Unify follow state into `FollowOrchestrator.followedArtists` as the single source of truth
- Remove follow-tracking responsibility from BubblePool so it focuses purely on pool management
- Preserve atomicity of state changes and physical pool operations within `followArtist()`
- Maintain loose coupling between controllers using the existing callback pattern

**Non-Goals:**

- Adding a discovery slice to `@aurelia/state` Store (native Aurelia observation is sufficient; Store remains for onboarding/guest only)
- Merging onboarding and authenticated follow flows
- Adding localStorage persistence for follow state
- Changing the DnaOrbCanvas `followedIds` bindable pattern (it continues to receive the value externally)

## Decisions

### 1. Derive `followedIds` from `followedArtists` via a getter

**Choice**: Implement `FollowOrchestrator.followedIds` as `new Set(this.followedArtists.map(a => a.id))`.

**Rationale**: Eliminates dual management of a Set and an Array. Aurelia detects property assignment (`this.followedArtists = [...]`) and re-evaluates the getter. Template bindings using `followedIds.has(artist.id)` update automatically via Aurelia's Set observation.

**Alternative rejected**: Adding a discovery slice to `@aurelia/state` Store — this would separate `dispatch()` from `pool.remove()`, breaking the atomicity that `markFollowed()` currently guarantees. It also works against Aurelia's native reactivity model.

**Performance**: With < 100 followed artists, the cost of creating a new Set on each access is negligible. If profiling reveals an issue, `@computed` can cache the result.

### 2. Inject `followedIds` into `BubblePool.dedup()` as a parameter

**Choice**: `dedup(bubbles: ArtistBubble[], followedIds: ReadonlySet<string>): ArtistBubble[]`

**Rationale**: Since BubblePool no longer tracks follow state, the caller must provide it externally. BubblePool remains a plain class with no DI dependency and stays independently testable.

**Affected call sites**: `BubbleManager` and `GenreFilterController` both call `pool.dedup()`.

### 3. Inject `getFollowedIds` callback into `BubbleManager`

**Choice**: Add `getFollowedIds: () => ReadonlySet<string>` to the constructor.

**Rationale**: BubbleManager is a plain class (no DI). This follows the existing callback pattern (`BubbleArtistClient`, `ILogger`). DiscoveryRoute passes `() => this.follow.followedIds` (lazy evaluation avoids construction-order issues).

**Alternative rejected**: Injecting FollowOrchestrator directly into BubbleManager — risks circular dependency and complicates unit tests.

### 4. GenreFilterController derives `followedIds` from its existing `followedArtists` callback

**Choice**: GenreFilterController already receives `followedArtists: () => ArtistBubble[]`. At the `pool.dedup()` call site, derive `new Set(this.followedArtists().map(a => a.id))` and pass it.

**Rationale**: No new callback required; existing interface is sufficient.

### 5. Preserve atomicity of state changes and physical pool operations

**Choice**: Within `followArtist()`, execute `followedArtists` update and `pool.remove()` synchronously in the same method.

```ts
// follow
this.followedArtists = [...this.followedArtists, artist]  // state change
this.pool.remove(artist.id)                                // physical operation

// rollback
batch(() => {
  this.followedArtists = this.followedArtists.filter(b => b.id !== artist.id)
  this.pool.add([artist])
})
```

**Rationale**: Preserves the atomicity currently guaranteed by `markFollowed()` while making each operation explicit. `batch()` on rollback defers Aurelia binding updates, preventing intermediate state from reaching the template.

### 6. Keep `followedArtists` typed as `ArtistBubble[]`

**Choice**: Do not extract a minimal type (`{ id, name, mbid }`).

**Rationale**: FollowOrchestrator is a UI-layer class, not a persistent Store. Keeping `ArtistBubble` avoids unnecessary conversion when passing to `BubbleManager.loadInitialArtists()` and allows reusing the original object for rollback bubble restoration.

## Risks / Trade-offs

**[Risk] `followedIds` getter creates a new `Set` on every access** — With < 100 entries this is negligible. If profiling shows a problem, add `@computed('followedArtists')` for caching.

**[Risk] Aurelia property-assignment detection may not trigger getter re-evaluation** — The existing pattern `this.followedArtists = [...this.followedArtists, artist]` is already proven to work. Aurelia detects property reference changes reliably.

**[Trade-off] Dual management of `guest.follows` and `followedArtists` remains** — Intentionally separated due to different lifecycles (localStorage persistence vs session-scoped). `FollowServiceClient` acts as a bridge, dispatching `guest/follow` during onboarding.

## Test Plan

All tests run with Vitest. The plan consists of updating existing test files and adding new test cases.

### 1. BubblePool (`test/services/bubble-pool.spec.ts`) — update existing tests

**Tests to remove:**

- Entire `markFollowed / unmarkFollowed / isFollowed` describe block
- `pool.isFollowed()` / `pool.markFollowed()` assertions within `reset`
- Tests in `dedup` that use `pool.markFollowed('a1')`

**Tests to modify:**

| Test | Before | After |
|------|--------|-------|
| `dedup > should filter out followed artists` | `pool.markFollowed('a1')` then `pool.dedup([...])` | `pool.dedup([...], new Set(['a1']))` |
| `reset > should clear pool and seen sets` | `pool.markFollowed()` + `pool.isFollowed()` assertions | Remove follow-related assertions; verify only seen sets + pool clearing |

**Tests to add:**

```
describe('dedup with external followedIds')
  - dedup(bubbles, followedIds) excludes artists present in followedIds
  - dedup(bubbles, emptySet) works without follow filtering
  - dedup(bubbles, followedIds) applies both seen and followed filters
```

### 2. FollowOrchestrator (`test/routes/discovery/follow-orchestrator.spec.ts`) — update existing tests

**Existing test modifications:**

Current tests depend on `pool.markFollowed()` / `pool.unmarkFollowed()` side effects. After the change, assertions shift to `pool.remove()` / `pool.add()` and direct `followedArtists` array operations.

| Test | Assertion change |
|------|-----------------|
| `should follow artist and update state optimistically` | `pool.isFollowed('a1')` → `sut.followedIds.has('a1')` (no change — already uses this pattern) |
| `should skip if artist already followed` | Verify guard uses `sut.followedIds.has()` |
| `should rollback on failure` | `pool.followedIds.has('a1')` → `sut.followedIds.has('a1')` (derived getter) |
| `should remove artist from pool on follow` | No change (`pool.availableBubbles` assertion remains valid) |

**Tests to add:**

```
describe('followedIds derived getter')
  - followedIds is an empty Set when followedArtists is empty
  - followedIds.has(id) returns true after followArtist
  - followedIds matches followedArtists.map(a => a.id)
  - followedIds is ReadonlySet (compile-time verification)

describe('atomicity — state and pool are synchronized')
  - after followArtist: followedArtists.length === 1 and artist is absent from pool
  - after rollback: followedArtists.length === 0 and artist is restored to pool

describe('duplicate follow prevention')
  - following the same artist twice results in only one entry in followedArtists
  - second followArtist call does not invoke followClient.follow
```

### 3. BubbleManager (`test/routes/discovery/bubble-manager.spec.ts`) — reflect constructor change

**Update all tests in beforeEach:**

```ts
// Before
sut = new BubbleManager(mockClient, createMockLogger())

// After
sut = new BubbleManager(mockClient, createMockLogger(), () => followedIds)
```

Initialize `followedIds` as `new Set<string>()` and populate per test case.

**Existing test modifications:**

| Test | Change |
|------|--------|
| `pool state sync > should expose followedIds through pool` | **Delete** — BubbleManager no longer exposes a `followedIds` getter |
| `loadInitialArtists > should deduplicate against followed artists` | Set `followedIds` via external Set instead of pool internal state |

**Tests to add:**

```
describe('dedup uses external followedIds')
  - loadInitialArtists passes getFollowedIds() to pool.dedup
  - onNeedMoreBubbles (inside getSimilarArtists) passes getFollowedIds() to pool.dedup
  - loadReplacementBubbles passes getFollowedIds() to pool.dedup
  - getFollowedIds returns the latest value at call time (lazy evaluation verification)
```

### 4. GenreFilterController (`test/routes/discovery/genre-filter-controller.spec.ts`) — reflect dedup parameter change

**Tests to add:**

```
describe('dedup with followed artists')
  - reloadWithTag passes followedIds derived from followedArtists() to pool.dedup
  - followed artists are excluded by dedup
```

### 5. Regression — prevent dual-state desync recurrence

**Tests to add (FollowOrchestrator):**

```
describe('regression: no dual-state desync')
  - after followArtist: IDs in followedIds do not appear in pool.availableBubbles
  - after rollback: IDs absent from followedIds are restored in pool.availableBubbles
  - sequential follow (3 artists) → rollback (1 artist) → followedIds.size === 2
    and only the rolled-back artist is restored to pool
```

### 6. Existing test coverage check

Tests potentially affected by the change but requiring no direct modification:

| Test file | Impact | Action |
|-----------|--------|--------|
| `test/routes/discovery-route.spec.ts` | BubbleManager constructor change | Update mock only if needed |
| `test/routes/discovery/concert-search-tracker.spec.ts` | None | No change |
| `test/routes/discovery/search-controller.spec.ts` | None | No change |
| `test/state/reducer.spec.ts` | None (no Store changes) | No change |
| E2E `e2e/onboarding-flow.spec.ts` | Follow flow validation | Verify after change (runs in CI) |

### 7. Final verification

- [x] `make check` (lint + test) passes
- [x] Grep confirms no remaining references to `pool.markFollowed` / `pool.unmarkFollowed` / `pool.isFollowed` / `pool.followedIds` across all test files
