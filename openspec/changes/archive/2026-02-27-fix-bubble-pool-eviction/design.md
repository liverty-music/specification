## Context

The artist discovery page uses a physics-based bubble UI where users tap artist bubbles to follow them. On tap, the system calls `ArtistService.ListSimilar` to fetch related artists and adds them to the bubble pool for continued exploration.

The current implementation has a critical bug: `getSimilarArtists()` pushes ~80 new artists into `availableBubbles` before the overflow calculation runs, causing the eviction logic to remove nearly all existing bubbles. The result is that all bubbles visually disappear on first tap.

Additionally, the initial load always fetches from `ListTop` regardless of whether the user already follows artists — missing the opportunity to show personalized recommendations.

## Goals / Non-Goals

**Goals:**
- Fix the bubble eviction bug so only a controlled number of oldest bubbles are removed on tap
- Implement following-count-based branching for initial load (top chart vs seed-based similar)
- Add `limit` parameter to `ListSimilar` and `ListTop` RPCs to control response size
- Ensure all array mutations use reassignment for Aurelia 2 reactivity

**Non-Goals:**
- Changing the physics engine or rendering logic (Matter.js / Canvas)
- Modifying the absorption animation or orb visual effects
- Adding pagination or infinite scroll to the bubble pool
- Changing the `ArtistService.Follow` or `ArtistService.Unfollow` RPCs

## Decisions

### 1. Pool management via `addToPool()` instead of direct mutation

The new `addToPool(newBubbles)` method atomically evicts oldest bubbles and inserts new ones using array reassignment (`this.availableBubbles = [...]`). This replaces the split `evictOldest()` + manual `push()` pattern.

**Rationale**: A single method eliminates the race between eviction and insertion that caused the bug. Array reassignment triggers Aurelia 2's property observation, which `push()`/`splice()` do not.

**Alternative considered**: Aurelia's `@observable` decorator — not needed because array reassignment already triggers observation, and the service doesn't need `xxxChanged` callbacks.

### 2. `getSimilarArtists()` as a pure fetch (no pool mutation)

The method now returns new bubbles without modifying `availableBubbles`. The caller (`DnaOrbCanvas.handleInteraction()`) is responsible for calling `addToPool()`.

**Rationale**: Separating fetch from pool mutation gives the caller control over eviction timing. This is the direct fix for the root cause — the old code mutated the pool inside the fetch, making overflow calculation stale.

### 3. Seed-based initial load when followed > 0 (Step 1-b)

When the user follows artists, randomly pick up to 5 seed artists and call `ListSimilar(limit = 50/seedCount)` in parallel. This replaces the unconditional `ListTop` call.

**Rationale**: Users who already follow artists get personalized recommendations instead of generic charts. The random selection with `Promise.all` keeps latency comparable to a single RPC call.

### 4. `limit` field added to proto messages (additive, non-breaking)

`int32 limit` is added to `ListSimilarRequest` (field 2) and `ListTopRequest` (field 3) with validation `{gte: 0, lte: 100}`. When 0 or omitted, the server uses its default.

**Rationale**: Additive field addition is backward-compatible. Existing clients that omit `limit` get the same behavior as before. The `lte: 100` constraint prevents abuse.

## Risks / Trade-offs

- **[Stale generated code]** The BSR-generated TypeScript and Go stubs won't include the `limit` field until the proto is published to BSR and regenerated. → Mitigation: Backend handler uses `0` placeholder with TODO comments until proto is regenerated. Frontend uses the field optimistically (Connect-RPC ignores unknown fields gracefully).

- **[Seed selection randomness]** Step 1-b picks random seeds, so the bubble pool varies between page loads. → Acceptable: This adds variety to the discovery experience, which is desirable.

- **[Promise.all failure mode]** If one seed's `ListSimilar` fails, that seed's results are lost but others proceed. → Mitigation: Each seed has an independent `.catch()` that returns `[]`, so partial failures degrade gracefully.
