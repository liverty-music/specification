## Why

The Discovery page's `DiscoveryRoute` component (680 LOC) is a God Component that manages three independent state layers — `BubblePool` (logical pool), `BubblePhysics` (Matter.js bodies), and component-level properties — with no synchronization guarantee. This desync causes a concrete bug: following an artist from search spawns a physics bubble at (0,0) due to a `display: none` timing issue, creating phantom off-screen bodies that inflate the bubble count and progressively reduce visible bubbles with each search-follow. The root cause is structural: the state architecture makes desync inevitable rather than impossible.

## What Changes

- Introduce a unified `BubbleManager` that owns both pool state and physics state, making desync structurally impossible.
- Extract domain concerns from `DiscoveryRoute` into focused controllers: `SearchController`, `GenreFilterController`, `FollowOrchestrator`.
- Reduce `DiscoveryRoute` from ~680 LOC / 27+ state properties to ~200 LOC of pure UI orchestration.
- Fix the search-follow absorption bug by deferring canvas reads until the element is visible.
- Replace imperative state mutations with observable patterns for Aurelia 2 change detection.
- Add comprehensive unit tests for each extracted module.

## Capabilities

### New Capabilities

- `bubble-state-management`: Unified bubble lifecycle management (pool + physics) via BubbleManager, ensuring single source of truth for bubble count, spawn position, and eviction.

### Modified Capabilities

- `search-follow-absorption`: Fix the spawn-at-origin bug by ensuring canvas visibility before reading `canvasRect`. Add canvas-ready guard to the absorption flow.
- `bubble-pool-lifecycle`: Pool mutations now go through BubbleManager which synchronizes physics bodies, replacing the current independent `BubblePool` class.
- `bubble-replenishment`: Replenishment trigger (`need-more-bubbles`) now flows through BubbleManager instead of being coordinated by DiscoveryRoute.

## Impact

- **Frontend code**: Major refactor of `src/routes/discovery/discovery-route.ts`, `src/services/bubble-pool.ts`, `src/components/dna-orb/dna-orb-canvas.ts`, `src/components/dna-orb/bubble-physics.ts`.
- **New files**: `BubbleManager`, `SearchController`, `GenreFilterController`, `FollowOrchestrator` classes.
- **Test files**: New unit tests for each extracted module; existing discovery tests updated.
- **No API/backend changes**: This is a frontend-only refactor.
- **No breaking changes to user-facing behavior**: All existing discovery interactions preserved.
