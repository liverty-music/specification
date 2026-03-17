## Context

The Discovery page is powered by a single `DiscoveryRoute` component (680 LOC) that acts as a God Component — directly managing bubble pool state, physics coordination, search UI, genre filtering, follow logic, concert search tracking, and onboarding flow. Three independent state layers (`BubblePool`, `BubblePhysics.bubbleMap`, and component properties) have no synchronization guarantee, causing a concrete bug where search-follow spawns phantom off-screen physics bodies that progressively reduce visible bubbles.

**Current architecture:**
```
DiscoveryRoute (680 LOC, 27+ state properties, 25+ methods)
├── BubblePool (plain class, no observability)
├── DnaOrbCanvas
│   ├── BubblePhysics (imperative, bubbleMap)
│   ├── OrbRenderer
│   └── AbsorptionAnimator
├── Search state (query, results, debounce timer)
├── Genre filter state (activeTag, isLoadingTag)
├── Follow state (followedArtists[], followedIds, optimistic rollback)
└── Concert search tracking (concertSearchStatus, timeouts)
```

**Constraints:**
- Aurelia 2 change detection requires reference changes on arrays/objects (mutating in place is invisible)
- `BubblePool.evictOldest()` uses `splice()` which mutates without reference change
- `display: none` on `.bubble-area` during search mode causes `getBoundingClientRect()` to return zeros
- Matter.js bodies spawned at (0,0) tunnel through walls, creating phantom off-screen bodies
- `artistsChanged()` only adds — never removes — creating one-way desync between pool and physics

## Goals / Non-Goals

**Goals:**
- Eliminate pool↔physics desync by making `BubbleManager` the single source of truth for bubble lifecycle
- Fix the search-follow absorption bug (`display: none` → canvasRect returns zeros)
- Reduce `DiscoveryRoute` to ~200 LOC of pure UI orchestration
- Extract testable units: each controller/manager is unit-testable with mocked dependencies
- Preserve all existing user-facing behavior (bubble tap, search follow, genre filter, onboarding)

**Non-Goals:**
- Replacing `@aurelia/state` or changing the global store architecture
- Changing the Canvas/Matter.js rendering approach
- Modifying backend APIs or protobuf definitions
- Redesigning the visual appearance of the discovery page
- Changing the `DnaOrbCanvas` rendering pipeline (layers, orb, absorption)

## Decisions

### 1. Unified BubbleManager owns pool + physics coordination

**Decision:** Create a `BubbleManager` class that wraps `BubblePool` and coordinates with `BubblePhysics` through `DnaOrbCanvas`, ensuring every pool mutation has a corresponding physics mutation.

**Rationale:** The root cause of the desync bug is that `BubblePool` and `BubblePhysics` are mutated independently by `DiscoveryRoute`. By funneling all operations through `BubbleManager`, desync becomes structurally impossible.

**Target architecture:**
```
DiscoveryRoute (~200 LOC, UI wiring only)
├── BubbleManager              ← NEW: single source of truth
│   ├── BubblePool             (dedup, capacity, seen tracking)
│   └── coordinates DnaOrbCanvas (physics add/remove/fade/spawn)
├── SearchController           ← NEW: search UI state + debounce
├── GenreFilterController      ← NEW: genre tag state + reload
├── FollowOrchestrator         ← NEW: follow RPC + optimistic rollback
├── ConcertSearchTracker       ← NEW: concert search status + coach mark
└── DnaOrbCanvas               (rendering + physics, unchanged public API)
```

**Alternative considered:** Using `IEventAggregator` to broadcast state changes — rejected because it adds indirection without solving the core desync (both pool and physics still need coordinated updates, events just add a layer between them).

**Alternative considered:** Moving all state into `@aurelia/state` — rejected because bubble physics state (Matter.js bodies, positions, velocities) is inherently imperative and frame-rate-driven, unsuited to a Redux-style reducer.

### 2. Canvas-ready guard for search-follow absorption

**Decision:** `BubbleManager.spawnAndAbsorb()` will wait for the canvas element to become visible before reading `canvasRect`. Use `requestAnimationFrame` after setting `isSearchMode = false` to guarantee the DOM has flushed `display: none` → `display: block` before measuring.

**Rationale:** The bug occurs because Aurelia's DOM flush is asynchronous (microtask), but `canvasRect` is read synchronously after `exitSearchMode()`. A single `requestAnimationFrame` guarantees layout has been recalculated.

**Alternative considered:** Using `visibility: hidden` instead of `display: none` — rejected because it still occupies layout space, breaking the search result list design.

### 3. Plain classes with constructor injection (not Aurelia DI)

**Decision:** `BubbleManager`, `SearchController`, `GenreFilterController`, `FollowOrchestrator`, and `ConcertSearchTracker` are plain TypeScript classes instantiated by `DiscoveryRoute` with explicit constructor parameters. They are NOT registered in Aurelia's DI container.

**Rationale:** These classes have the same lifetime as `DiscoveryRoute` (created on route load, destroyed on leave). Using Aurelia DI would make them singletons or require complex scoping. Plain construction makes dependencies explicit, lifetimes obvious, and unit testing trivial (no DI container setup needed).

### 4. DnaOrbCanvas public API unchanged

**Decision:** `DnaOrbCanvas` keeps its existing public methods (`spawnBubblesAt`, `spawnAndAbsorb`, `fadeOutBubbles`, `reloadBubbles`, `pause`, `resume`, `canvasRect`, `bubbleCount`). `BubbleManager` calls these methods directly via the component reference.

**Rationale:** `DnaOrbCanvas` is a well-scoped rendering component. Its API is already clean. The problem is not in Canvas but in how `DiscoveryRoute` coordinates pool↔canvas. Adding indirection would increase complexity without benefit.

### 5. Observable array patterns for Aurelia change detection

**Decision:** All array mutations in `BubbleManager` and controllers produce new array references (spread, filter, map) rather than mutating in place. `BubblePool.evictOldest()` will be changed from `splice()` to return evicted items without mutation, with the caller replacing the array.

**Rationale:** Aurelia 2's `@bindable` and `@watch` detect reference changes, not deep mutations. The current `splice()` in `evictOldest` is invisible to Aurelia, causing stale template bindings.

## Risks / Trade-offs

**[Risk] Increased file count** → Mitigation: Each new file is small (50-150 LOC), focused, and independently testable. Net LOC stays similar or decreases. The trade-off is worth it for testability and maintainability.

**[Risk] Coordination overhead between controllers** → Mitigation: `DiscoveryRoute` remains the single orchestration point — controllers don't reference each other. Data flows top-down: `DiscoveryRoute` → controllers → `DnaOrbCanvas`.

**[Risk] `requestAnimationFrame` delay for search-follow absorption** → Mitigation: The delay is a single frame (~16ms), imperceptible to users. The absorption animation itself takes ~400ms, so the 16ms wait is invisible.

**[Risk] Breaking existing behavior during refactor** → Mitigation: Specs define exact behavior contracts. Unit tests for each extracted module verify behavior independently. E2E tests verify the integrated flow.
