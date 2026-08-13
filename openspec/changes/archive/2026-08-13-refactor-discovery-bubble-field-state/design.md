## Context

The Discovery bubble field is represented across independently-mutable stores kept in sync by an imperative reconcile:

- `ArtistStore.lastBubbles` — app-lifetime snapshot for instant re-entry paint
- `ArtistStore` `CachedResource<listTop>` — separate SWR cache of raw RPC
- `BubblePool.availableBubbles` — per-route working pool (recreated each re-entry via `new BubbleManager`)
- `BubblePhysics.bubbleMap` — the actual on-screen bodies (the real "what's visible")
- `FollowStore.followedIds` — follow state used to filter in 3–4 places

Invariants (exclude-followed, 50-cap, dedup) are re-implemented at multiple sites with different semantics: cap is `evict-oldest` in the pool, `slice` in the manager, and a silent `break` in physics. Because model (pool) and view (bubbleMap) are separate stores synced by a lossy one-way reconcile (`artistsChanged`), they diverge. A prod re-entry with 6 follows reproduces pool=33 but physics=16: the background load replaces the pool wholesale, `artistsChanged` fades ~41 old bodies and calls `addBubbles(newSet)`, but the physics cap counts the still-fading bodies and `break`s, silently dropping ~17 artists that are never retried. Separately, re-entry always re-derives the field (seed-similar when followed), so a full field collapses on return.

This change is frontend-only. No proto/API/backend change.

## Goals / Non-Goals

**Goals:**
- One authoritative owner of the display field; physics/cache derive from it.
- Physics becomes a pure projection: `reconcile(target)` with no cap/dedup/followed policy; render parity (bodies == field at rest) guaranteed even across background refresh.
- Invariants applied exactly once at the field boundary.
- Re-entry preserves the in-session field (TTL-fresh reuse + non-destructive delta) instead of wholesale replace.
- Encode the Aurelia observation contract so the fix cannot silently regress.

**Non-Goals:**
- Web Worker / OffscreenCanvas physics offload (the `reconcile(target)` boundary is designed to enable it later, but it is out of scope here).
- Redesigning the seed-similar recommendation logic itself (only *when* it runs changes).
- Changing the 50-bubble cap value or the tap/absorption/search UX.
- `content-visibility` based pause (current `visibilitychange` pause/resume is retained; CV is a later enhancement needing an IntersectionObserver fallback).

## Decisions

### D1: A single field owner (`ArtistBubbleStore`), physics is a pure projection
Introduce one owner of `field: Artist[]`. It applies the invariants (exclude-followed + dedup + cap) in one place when producing/updating the field. `BubblePhysics` gains `reconcile(target: Artist[])` that diffs `bubbleMap` against the target (keep/remove/add) and **removes the MAX-cap `break` and fading-body counting**. `BubblePool` is reduced to a pure dedup/cap helper (or folded into the owner) — it no longer holds a second authoritative copy.

- **Alternative considered:** keep pool+physics separate and just fix the cap counting. Rejected — it patches the symptom (⑤) but leaves the divergence architecture (pool≠physics can still drift on any future path) and the duplicated invariants.
- **Owner lifetime:** app-lifetime DI singleton (`DI.createInterface(..., x => x.singleton(...))`) so it survives the per-route component churn and can hold the session-preserve state.

### D2: Aurelia observation contract (prevents regression)
- The field is handed to the canvas as an **immutable snapshot (new array reference)** on every update. Aurelia's `[bindable]Changed` (`artistsChanged`) fires on reference change, not in-place mutation — so a new reference guarantees deterministic propagation. (The "never immutably replace domain state" rule does not apply: this is a derived *view projection*, not the source of truth.)
- Multi-step field updates use `batch()` so `@observable` sync notifications collapse into one reconcile.
- The reconcile applies physics changes aligned to the render loop / async flush — heavy work does not run synchronously inside the bindable callback (INP).
- Separate concerns by lifecycle: router `loading()` only requests a field update on the owner; the canvas initializes from the owner's current snapshot in `attached()` (bottom-up, after the owner is ready) and reacts to subsequent changes. This removes the current `loading()`-before-canvas-attached ordering hazard.

- **Alternative considered:** inject the field store directly into `dna-orb-canvas` and observe via `@watch`/`IObservation` instead of the `artists` bindable. Rejected as the default to keep the canvas presentational/testable; the bindable-snapshot contract achieves the same determinism. (Kept as a fallback if binding timing proves fragile.)

### D3: Re-entry preserves the field via non-destructive delta
On re-entry, if the cached field is fresh (within TTL) the owner reuses it and applies only: (a) remove newly-followed artists, (b) top-up **only** if below the display floor. No wholesale `replace()`. A stale (TTL-expired) field falls back to a full cold-style reload. TTL reuses the existing SWR staleness concept so there is a single freshness notion.

- **Alternative considered:** keep the wholesale background replace but make it additive/stable. Rejected — replace inherently recomposes (seed-similar vs top) and is the root of the collapse; a delta is the minimal correct behavior.

### D4: Collapse the two caches
Remove `ArtistStore.lastBubbles`. The single bubble-field cache is owned by `ArtistBubbleStore` (derived from the SWR `listTop` results after invariants). `ArtistStore` keeps only the raw-RPC SWR cache and is renamed conceptually to a repository role (rename optional/cosmetic, can defer).

## Risks / Trade-offs

- **[Risk] Behavior change: re-entry no longer re-rolls the field** → This is intended (proposal marks it BREAKING-UX). Mitigation: TTL-expiry still gives a fresh field periodically; the display floor keeps it full.
- **[Risk] Removing the physics cap `break` could exceed 50 bodies if the field owner fails to cap** → Mitigation: cap is enforced at the field boundary (D-invariant), and physics keeps a *logged* hard safety ceiling (never a silent drop) per the spec.
- **[Risk] Immutable-snapshot reassignment churns GC / re-runs reconcile** → Mitigation: reconcile is a diff (only add/remove deltas touch physics); array allocation of ≤50 refs per update is negligible.
- **[Risk] Singleton field store leaking subscriptions across route churn** → Mitigation: canvas/route unsubscribe in `detaching`/`unbinding`; do not mutate `@observable` in `unbinding`.
- **[Risk] Scope creep into seed-similar/worker** → Explicit Non-Goals; the `reconcile(target)` boundary is the only worker-enabling seam introduced.

## Migration Plan

Frontend-only; ships behind normal release. Phased so the visible bug is fixed early and independently:

1. **Phase 0 (stop-the-bleed, independently shippable):** in `BubblePhysics`, make `reconcile(target)` a diff and stop counting fading-out bodies against capacity (remove the silent `break`). Restores render parity (physics == field) without the larger refactor.
2. **Phase 1 (single source of truth):** introduce `ArtistBubbleStore`, fold pool/`lastBubbles` into it, apply invariants once, wire the Aurelia snapshot/`batch()` contract.
3. **Phase 2 (preserve on re-entry):** TTL-fresh reuse + non-destructive delta; remove wholesale replace.
4. **Phase 3 (cleanup):** collapse caches, remove duplicated dedup/cap/followed sites, optional `ArtistStore`→repository rename.

Rollback: each phase is a separate PR/release; revert the offending phase. No data migration.

## Open Questions

- Display floor value and TTL for re-entry reuse — reuse the existing SWR `staleTime` (24h) or a shorter session-scoped TTL? (Leaning: session-scoped freshness for reuse, SWR TTL for the raw cache.)
- Should `ArtistBubbleStore` be a true app singleton or a session-scoped store cleared on sign-out (to avoid cross-user field bleed)? (Leaning: singleton that clears on the same `SignedOut` event `FollowStore` already listens to.)

## Phase 1 Detailed Design

Refines decision D1 for the Phase 1 implementation. Goal: one owner of the display field with the invariants applied exactly once, consistent with the codebase's "singleton service owns its `@observable` state and behavior" pattern (FollowStore, ConcertStore).

### D5: `ArtistBubbleStore` owns fetch orchestration **and** the field — no separate manager layer

The store (DI app-singleton) is the single owner of the discovery field lifecycle: it calls the artist repository (`listTop`/`listSimilar`), applies the invariants once, and holds the field. The per-route `BubbleManager` is removed — its fetch logic (initial load, seed-similar + top-up, reset, similar-on-tap, replacement) moves into the store as fetch methods. This removes an intermediary layer and keeps a single owner rather than a per-route fetcher plus a singleton store.

- **Alternative considered:** keep `BubbleManager` as a per-route fetcher feeding the store. Rejected — two objects sharing responsibility for the field lifecycle is exactly the split this change removes; a singleton that owns fetch + invariants + state matches the existing store pattern.

```ts
export const IArtistBubbleStore = DI.createInterface<IArtistBubbleStore>(
  'IArtistBubbleStore', x => x.singleton(ArtistBubbleStore))

// Owns the display FIELD (Artist[]) — the authoritative set of artists to show.
// It does NOT own physics bodies or render state (those derive from the field via
// the canvas reconcile); "Bubble" in the name is the feature's ubiquitous language,
// not a claim that this store holds bodies.
export class ArtistBubbleStore {
  private readonly artists = resolve(IArtistStore)
  private readonly followStore = resolve(IFollowStore)
  @observable public field: readonly Artist[] = []   // frozen snapshot, reassigned
  private readonly seen = new Set<string>()          // retired/shown ids (dedup memory)

  // fetch orchestration (formerly BubbleManager) — seeds come from followStore.followedArtists
  loadInitial(country, tag): Promise<void>           // listTop | seed-similar(followedArtists) + top-up → setField
  reset(country): Promise<void>                      // listTop('') → setField
  loadSimilar(artistId): Promise<Artist[]>           // listSimilar (in-flight guarded) → addAt candidates
  // field mutation — the ONLY place invariants are applied
  private setField(candidates: Artist[]): void
  addAt(candidates: Artist[], pos?: {x,y}): Artist[] // top-up; returns actually-added (carries placement hint to reconcile)
  remove(artistId): void
  paintFromCache(cached: Artist[]): void
}
```

Seed-similar needs the followed **`Artist[]`** (id + name) as seeds, not just ids — the store reads `followStore.followedArtists` (the observable list), NOT `followedIds` (a `ReadonlySet<string>`).

### D6: invariants as pure functions + a `seen` `Set` (drop `BubblePool`-as-helper)

The invariants live in one private path used by every mutation. **Followed-exclusion runs over the whole field (kept + candidates), not just candidates** — otherwise an artist already in `keep` that the user has since followed lingers on the field (the #737 followed-bubble-residue class). **`capTo` truncates the TAIL** so `keep` (placed first) retains priority — the opposite of the current `BubblePool.evictOldest`/`add`, which drop from the front; the store must not reuse that front-eviction semantics.

```ts
private applyInvariants(candidates, keep: readonly Artist[]): Artist[] {
  const followed = this.followStore.followedIds
  const merged = dedupById([...keep, ...candidates]) // intra-array dedup, keep wins ties
  return capTo(excludeFollowed(merged, followed), MAX_BUBBLES) // exclude over WHOLE field; drop from tail
}
```

**The cap eviction direction is operation-dependent — a single `capTo` cannot serve both flows** (resolved during Phase 1 review):

- **`setField` family** (full replace: initial load, cache re-entry paint, genre, reset, background refresh): tail-drop with **keep-priority** — `applyInvariants(candidates, keep)` places `keep` first so an over-cap drops candidates, **never the currently-visible field**. This is what prevents the "return and the field shrank" collapse (#737).
- **`addAt` (tap similar top-up)**: the OPPOSITE — new similar candidates MUST win, and the **oldest existing bodies are evicted (FIFO) with a fade** to make room (preserving the current `addBubblesWithEviction` UX). Applying keep-priority here would drop the new similar candidates and the tap would surface almost nothing (a full field + 30 similar → only 1 admitted). So `addAt` orders candidates first and evicts oldest existing: `capTo(dedupById([...freshCandidates, ...existingNewestFirst]), MAX_BUBBLES)`, then the evicted (existing not in the result) fade out via reconcile removals.

`MAX_BUBBLES` (50) moves out of the retired `BubblePool` into the pure-invariants module alongside `dedupById`/`excludeFollowed`/`capTo`; `bubble-physics.ts` imports it from there.

`dedupById` / `excludeFollowed` / `capTo` are pure, unit-testable functions. `capTo(xs, n)` returns `xs.slice(0, n)` (tail-drop). Unit tests lock: (a) a `keep` member that becomes followed is removed; (b) over-cap drops candidates, never `keep`. The current `BubblePool` (a second stateful membership copy) is **not** reused as a helper — that conflated names and roles. `dedupById` de-duplicates **within the input array** (by id, then name/mbid), which fixes the shipped duplicate bug ([bubble-pool.ts `dedup`](../../../frontend/src/services/bubble-pool.ts) filtered against a seen-set but never removed intra-array dupes, so seed-similar `results.flat()` let cross-seed artists through — prod showed Vaundy×3). `seen` is a plain `Set<id>` cleared on `reset`.

### D7: observation contract — reassignment is the correct trigger for the imperative canvas

`field` is `@observable` and is **reassigned to a new frozen array** on every update. This is deliberately *not* the "mutate the property" guidance that applies to DOM-bound state: the canvas is an imperative Matter.js renderer consumed through `@bindable artists` + the `artistsChanged` **property-change callback**, which fires only on reference change (collection mutation would not trigger it). So the store→canvas boundary is a change-notification bus, not fine-grained DOM observation — reference replacement is the idiomatic trigger here. `discovery-route` binds `artists.bind="fieldStore.field"`; `artistsChanged` routes to `physics.reconcile(field)` (Phase 0). Multi-step updates use `batch()` so the synchronous `@observable` notifications collapse into one reconcile. The canvas stays a presentational bindable component (testable) rather than injecting the store.

### D8: animated placement is expressed through `reconcile`, not a separate spawn call

Because `field` is a synchronous `@observable`, reassigning it inside `addAt` fires `artistsChanged → reconcile(field)` **before** any follow-up `canvas.spawnBubblesAt(...)` — so reconcile would place the new body at a random position and the later `spawnBubblesAt` would no-op (`bubbleMap.has(id)`), losing the tap-origin animation. Rather than depend on a fragile call order, **generalize the mechanism**: `reconcile(target, opts?: { placements?: Map<id, {x,y}> })`. For a newly-added target id present in `placements`, reconcile spawns it at that position with the pop/outward animation (the current `spawnBubblesAt` behavior); otherwise it uses the instant random `addBubbles` placement. The store's `addAt(candidates, pos)` applies invariants, sets `field`, and carries the placement hint for the added ids through to reconcile. There is exactly one path into physics (reconcile) and no ordering contract.

Search **follow-and-absorb** (`spawnAndAbsorb`) is different — it is a transient flourish (the artist flies into the orb and is *not* added to the field). It stays an imperative canvas animation the route triggers on follow, alongside `store.remove(id)` for membership; it keeps its `requestAnimationFrame` + zero-rect guard (see D11).

### D9: Phase 1 leaves `ArtistStore.lastBubbles` in place, but physics has a single writer

Collapsing the two caches is Phase 3. During Phase 1 the store holds `field` while `ArtistStore.lastBubbles` still backs the instant re-entry paint, so complexity peaks mid-refactor: `lastBubbles` (raw cache) and the store `field` coexist transiently, shrinking to one after Phase 3. **Critically, the re-entry cache paint must go THROUGH the store**: `loading()` reads `peekBubbles()` and calls `store.paintFromCache(cached)`, which runs invariants and sets `field` → the single `reconcile` writer paints physics. Nothing writes `pool`/physics directly (no `pool.replace` + separate ghost paint). This keeps exactly one physics writer even while two caches coexist, so the dual-writer/ordering hazard D2 removes does not reappear. Phase 1 does not yet change *what* re-entry loads (still a full `setField`); the non-destructive delta is Phase 2.

### D10: singleton lifetime — reset boundaries (resolves Open Question #2)

The store is an app-lifetime DI singleton, so per-visit and per-user state must be reset explicitly (a per-route `new BubbleManager` reset these for free):

- **Sign-out:** subscribe to the `SignedOut` event `FollowStore` already handles and clear `field`, `seen`, and `country`. Prevents user A's field/dedup memory bleeding into user B on a shared singleton.
- **Route entry (`loading()`):** clear `seen` and re-detect `country` each Discovery entry, matching the current per-route reset. `field` is NOT cleared (it backs the instant re-entry paint); it is refreshed via `paintFromCache` + background `setField`. Not clearing `seen` per entry would accumulate across a long session and starve top-up (legitimately-new candidates filtered as "already seen").
- `seen` is also cleared inside `reset()` (genre/reset control), as today.

### D11: safeguards that MUST be re-homed from `BubbleManager` (implementation checklist)

Folding `BubbleManager` into the store must preserve, not drop, these existing behaviors (each gets a test):

1. **In-flight guard** (`isLoadingBubbles`): `loadSimilar`/`loadInitial` must lock out concurrent loads (rapid taps) so overlapping fetches don't double-add/over-evict — more important now that the owner is a singleton.
2. **Similar-exhausted recovery** (`loadReplacementBubbles` + `resetSeenWith`): when `listSimilar` returns nothing new, fall back to `listTop` after narrowing `seen` to the currently-visible field, so the field refills instead of firing the "unavailable" Snack every time.
3. **Canvas-hidden deferral** (`spawnAndAbsorbAfterSearch`): keep the `requestAnimationFrame` + zero-rect guard so a follow-absorb never reads a `0×0` canvas and spawns at `(0,0)`.
4. **FIFO eviction + fade choreography** (`addBubblesWithEviction`): at cap, evict the OLDEST bodies with the fade-out animation (via reconcile removals ordered oldest-first) rather than silently dropping candidates or removing arbitrary bodies.
5. **Seed-similar tuning**: `MAX_SEED_ARTISTS`, `pickRandomSeeds` shuffle, `limitPerSeed = floor(MAX/seeds)`, the `SEED_SIMILAR_TARGET` top-up floor, and the **per-seed `.catch(() => [])`** so one failed `listSimilar` doesn't reject the whole `Promise.all`.
6. **Caller migrations**: `GenreFilterController` calls `store.setField(listTop(tag))` instead of receiving a raw `pool`; the follow-failure rollback (`pool.add([artist])`) becomes `store.addAt([artist])`; `discovery-route.onArtistSelected` uses `store.remove(id)`.

### D12: hue is a per-artist derived value memoized in the render layer (heavy render optimization deferred)

The bubble color (`hue`) is a pure function of `artist.name`, currently recomputed **every frame per bubble** (`artistHue(name)` inside `renderBubble`, ~50×60/s). Phase 1 memoizes it **per artist in the canvas render layer** (`Map<artistId, hue>`), NOT on the `Artist` entity: `Artist` is a `readonly` proto-sourced domain type shared by dashboard/search/follow, so a canvas-only presentation value must not leak onto it (that would re-blur the layer separation this change enforces). The memo is keyed by artist id (falling back to name) so it survives the ghost→real reference swap and is computed once per artist. This is a self-contained, visually-identical change (same colors), safe to include in the Phase 1 PR without touching visual baselines.

**Deferred to a separate follow-up change (measure-first):** the heavier render-layer INP work — per-frame `createRadialGradient` allocation, per-frame `shadowBlur` rim blur, and per-frame text layout (`measureText` + font-shrink loop in `renderBubbleText`) — which is best addressed structurally by baking each bubble into a cached offscreen sprite (per artist + radius bucket) and `drawImage`-ing it per frame. That work changes pixels (requires visual-baseline regeneration) and should be profiled (Chrome DevTools + `modern-web-guidance`) to confirm the dominant cost before optimizing; bundling it with the SSoT refactor would mix pixel changes into a structural PR. At 50 bodies the physics step is NOT the bottleneck (Matter.js handles far more); the render layer is. Worker/OffscreenCanvas physics offload stays a Non-Goal — the `reconcile(target)` boundary keeps it possible later, but it is low-value at this scale and costly (synchronous tap hit-testing would need cross-thread coordination).
