## Why

The Discovery bubble field is represented in several independently-mutable stores (`ArtistStore.lastBubbles` cache, a per-route `BubblePool`, the `BubblePhysics.bubbleMap`, plus the `listTop` SWR cache), synchronized only by a lossy imperative reconcile. There is no enforced single source of truth, and the same invariants (exclude-followed, 50-cap, dedup) are re-implemented in 3–4 places with different semantics. As a result the rendered field can silently diverge from the data pool — a prod re-entry reproduces pool=33 but only 16 bubbles rendered — and the field the user was looking at is discarded and re-derived on every re-entry, so navigating away and back collapses a full field to a few bubbles. The existing `bubble-state-management` spec already asserts "pool count and physics body count SHALL be equal", but the implementation does not satisfy it.

## What Changes

- Establish a single owner of "the current display field" (`Artist[]`); the pool cache, physics bodies, and SWR cache all derive from it. Remove the duplicate `ArtistStore.lastBubbles` snapshot in favor of one cache.
- Make the physics/canvas layer a **pure projection** of the field: it reconciles its bodies to a target list and MUST NOT own the capacity cap, dedup, or followed-exclusion. Guarantee rendered-body count equals the field count at rest, including across background-refresh transitions (fixes the fading-body cap contention that silently drops bubbles).
- Apply the invariants (exclude-followed, 50-cap, dedup) exactly once, at the field-update boundary — not at each call site (`loading()`, `loadInitialArtists`, `genre`, `onArtistSelected`).
- Re-entry within a session preserves the field the user was viewing: reuse the existing field when fresh (within TTL) and apply a **non-destructive delta** (drop newly-followed, top-up only if below the floor) instead of a wholesale `pool.replace()` that shrinks and re-composes the field. **BREAKING (UX)**: returning to Discovery no longer re-rolls the bubble field.
- Encode the Aurelia observation contract so the fix does not regress: the display field propagates to the canvas as an immutable snapshot (reference change) so the change callback fires deterministically; multi-step updates use `batch()`; data fetch (router `loading`) is separated from view init (`attached`).

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `bubble-state-management`: enforce a real single source of truth — physics becomes a pure projection that reconciles to the field with no independent cap/dedup; rendered count equals field count at rest even during refresh; capacity/dedup/followed-exclusion applied once at the field boundary.
- `discovery-bubble-cache`: re-entry preserves the prior in-session field (TTL-fresh) and applies a non-destructive delta (remove followed, top-up below floor) rather than a full replace; collapse the two overlapping caches (`lastBubbles` + `listTop` SWR) into one.

## Impact

- Frontend only — no proto/API/backend change.
- `frontend/src/routes/discovery/` — `discovery-route.ts` (loading/loadInitialBubbles/onReset/onArtistSelected/onFollowFromSearch), `bubble-manager.ts`, `genre-filter-controller.ts`.
- `frontend/src/services/` — `artist-store.ts` (remove `lastBubbles`, keep single SWR cache), `bubble-pool.ts` (reduced to pure dedup/cap helper or folded into the field owner).
- `frontend/src/components/dna-orb/` — `dna-orb-canvas.ts` (`artistsChanged` → declarative reconcile), `bubble-physics.ts` (`reconcile(target)`; drop the MAX-cap `break` and fading-body counting).
- Related specs touched at the edges: `bubble-pool-lifecycle` (cap/dedup ownership), `artist-discovery-dna-orb-ui` (physics render parity). Unblocks a future Web-Worker/OffscreenCanvas split (the `reconcile(target)` boundary is serializable).
