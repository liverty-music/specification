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

### D1: A single field owner (`DiscoveryFieldStore`), physics is a pure projection
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
Remove `ArtistStore.lastBubbles`. The single bubble-field cache is owned by `DiscoveryFieldStore` (derived from the SWR `listTop` results after invariants). `ArtistStore` keeps only the raw-RPC SWR cache and is renamed conceptually to a repository role (rename optional/cosmetic, can defer).

## Risks / Trade-offs

- **[Risk] Behavior change: re-entry no longer re-rolls the field** → This is intended (proposal marks it BREAKING-UX). Mitigation: TTL-expiry still gives a fresh field periodically; the display floor keeps it full.
- **[Risk] Removing the physics cap `break` could exceed 50 bodies if the field owner fails to cap** → Mitigation: cap is enforced at the field boundary (D-invariant), and physics keeps a *logged* hard safety ceiling (never a silent drop) per the spec.
- **[Risk] Immutable-snapshot reassignment churns GC / re-runs reconcile** → Mitigation: reconcile is a diff (only add/remove deltas touch physics); array allocation of ≤50 refs per update is negligible.
- **[Risk] Singleton field store leaking subscriptions across route churn** → Mitigation: canvas/route unsubscribe in `detaching`/`unbinding`; do not mutate `@observable` in `unbinding`.
- **[Risk] Scope creep into seed-similar/worker** → Explicit Non-Goals; the `reconcile(target)` boundary is the only worker-enabling seam introduced.

## Migration Plan

Frontend-only; ships behind normal release. Phased so the visible bug is fixed early and independently:

1. **Phase 0 (stop-the-bleed, independently shippable):** in `BubblePhysics`, make `reconcile(target)` a diff and stop counting fading-out bodies against capacity (remove the silent `break`). Restores render parity (physics == field) without the larger refactor.
2. **Phase 1 (single source of truth):** introduce `DiscoveryFieldStore`, fold pool/`lastBubbles` into it, apply invariants once, wire the Aurelia snapshot/`batch()` contract.
3. **Phase 2 (preserve on re-entry):** TTL-fresh reuse + non-destructive delta; remove wholesale replace.
4. **Phase 3 (cleanup):** collapse caches, remove duplicated dedup/cap/followed sites, optional `ArtistStore`→repository rename.

Rollback: each phase is a separate PR/release; revert the offending phase. No data migration.

## Open Questions

- Display floor value and TTL for re-entry reuse — reuse the existing SWR `staleTime` (24h) or a shorter session-scoped TTL? (Leaning: session-scoped freshness for reuse, SWR TTL for the raw cache.)
- Should `DiscoveryFieldStore` be a true app singleton or a session-scoped store cleared on sign-out (to avoid cross-user field bleed)? (Leaning: singleton that clears on the same `SignedOut` event `FollowStore` already listens to.)
