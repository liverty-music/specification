## 1. Phase 0 — Stop-the-bleed: physics render parity (independently shippable)

- [x] 1.1 `bubble-physics.ts`: add `reconcile(target: Artist[])` that diffs `bubbleMap` vs target (keep matching ids, fade/remove ids not in target, add ids not present)
- [x] 1.2 `bubble-physics.ts`: stop counting fading-out bodies against capacity when adding; remove the silent `break` in `addBubbles` cap path (replace with a logged hard safety ceiling that never silently drops a target member)
- [x] 1.3 `dna-orb-canvas.ts`: route `artistsChanged` through `physics.reconcile(newVal)` instead of the fade-out + `revealGhostBubbles` + `addBubbles` sequence for the real-artist path
- [x] 1.4 Unit tests: reconcile converges body set to target; background-refresh transition ends with body count == field count (covers `bubble-state-management` "Background refresh preserves render parity" + "Physics never silently drops a target member"). Also added a revive-on-re-add regression test (mid-fade target member re-added within the fade window) per #514 review.
- [x] 1.5 `make check` green
- [x] 1.6 Frontend PR (#514) → CI green → merge → Release (v1.39.2) → prod roll (CP pin 850104b). Prod-verified via the live Aurelia VM: rendered physics bodies == UNIQUE pool artists, `inPoolButNotRendered=0`, no collapse. NOTE: raw `pool.length` > rendered because the pool still holds duplicates (seed-similar top-up dedup gap) — physics dedupes by id so the field is visually correct; the pool-level dedup is fixed by Phase 1 task 2.2 (invariants applied once). Also shipped deps PR #516 (dompurify ^3.4.13 override) to clear the repo-wide Security Audit gate.

## 2. Phase 1 — Single source of truth (ArtistBubbleStore)

- [x] 2.1 Add `ArtistBubbleStore` (DI app-singleton, `IArtistBubbleStore`) owning `field: Artist[]`, with a single `setField` path that applies invariants (exclude-followed + dedup + 50-cap) exactly once. Pure invariants (`dedupById`/`excludeFollowed`/`capTo`) + `MAX_BUBBLES` live in a standalone module; `seen` dedup memory (name/id/mbid) folds into the store.
- [x] 2.2 Move follow-exclusion, dedup, and cap out of `discovery-route.ts` `loading()`, `bubble-manager.ts`, and `genre-filter-controller.ts` into the store's single boundary (covers `bubble-state-management` "Bubble invariants are applied once at the field boundary")
- [x] 2.3 Two cap-eviction policies (per D6): `setField` family = tail-drop keep-priority (never evict the visible field); `addAt` (tap similar top-up) = FIFO evict-oldest with fade so new candidates win. Retire `BubblePool` (fold `MAX_BUBBLES` + seen memory into the store/invariants module); remove its role as a second authoritative membership store.
- [x] 2.4 Aurelia observation contract: store emits an immutable snapshot (new frozen array reference) on each update; wire the canvas to consume it so `artistsChanged` fires deterministically; wrap multi-step updates in `batch()`. `addAt(candidates, pos)` carries a placement hint through to `reconcile(target, { placements })` (D8) so tap-origin spawn animation is preserved with a single physics path.
- [x] 2.5 Separate lifecycle (D10): `loading()` only requests a field update (clears `seen`, re-detects `country`, `paintFromCache` + background `setField`); canvas initializes from the store snapshot in `attached()` and reconciles on change; unsubscribe in `detaching`/`unbinding`. Store subscribes to `SignedOut` and clears `field`/`seen`/`country`.
- [x] 2.6 Re-home the `BubbleManager` safeguards (D11): in-flight guard, similar-exhausted recovery, canvas-hidden rAF deferral, FIFO fade choreography, seed-similar tuning (`MAX_SEED_ARTISTS`/shuffle/`limitPerSeed`/`SEED_SIMILAR_TARGET`/per-seed `.catch`).
- [x] 2.7 Memoize `hue` per artist in the canvas render layer (`Map<artistId, hue>`, D12) — stops the per-frame `artistHue(name)` hash; visually identical (no baseline change). Do NOT put hue on the `Artist` entity.
- [x] 2.8 Unit tests: invariants applied once (no double-filter downstream); field↔physics parity on add/remove/evict; `addAt` FIFO keeps new similar + evicts oldest; `reconcile` placements; hue memo returns stable value across ghost→real swap (covers `bubble-state-management` SSoT scenarios)
- [x] 2.9 `make check` green
- [x] 2.10 Frontend PR → CI green → merge → Release → prod roll

> **Deferred (separate change, measure-first):** heavy render-layer INP optimization — per-frame gradient/`shadowBlur`/text-layout eliminated via cached offscreen bubble sprites. Changes pixels (needs visual-baseline regen) and must be profiled first; kept out of the Phase 1 SSoT PR. See design D12.

## 3. Phase 2 — Preserve the in-session field on re-entry

- [x] 3.1 Field store: on re-entry, if the cached field is fresh (within TTL) reuse it and apply a non-destructive delta (remove newly-followed, top-up only below the display floor); no wholesale `replace()`
- [x] 3.2 Field store: stale (TTL-expired) re-entry falls back to a full cold-style reload that still converges within capacity with render parity
- [x] 3.3 Remove the unconditional wholesale background `pool.replace()` on re-entry from `discovery-route.ts` / `bubble-manager.ts`
- [x] 3.4 Unit tests: fresh re-entry reuses field and does not shrink below prior count (minus follows); follow-while-away removes only the followed and tops up to floor (covers `discovery-bubble-cache` re-entry-preservation scenarios)
- [x] 3.5 `make check` green
- [x] 3.6 Frontend PR → CI green → merge → Release → prod roll; verify in prod: navigate away and back keeps the field (no collapse to a few bubbles), following an artist then re-entering removes only that artist

## 4. Phase 3 — Cleanup: collapse caches and duplicated logic

- [x] 4.1 Remove `ArtistStore.lastBubbles` (`peekBubbles`/`setBubbles`); the single bubble-field cache lives in `ArtistBubbleStore` derived from the SWR `listTop` results (covers `discovery-bubble-cache` single-cache requirement)
- [x] 4.2 Remove any remaining duplicated dedup/cap/followed-filter call sites; confirm the physics layer applies no policy
- [x] 4.3 (Optional) Rename `ArtistStore` to a repository role — SKIPPED (cosmetic symbol rename deferred per design; class doc already reflects the repository role)
- [x] 4.4 `make check` green
- [x] 4.5 Frontend PR → CI green → merge → Release → prod roll

## 5. Close-out

- [x] 5.1 Verify all delta spec scenarios are satisfied by the shipped implementation (render parity, invariants-once, re-entry preservation, single cache)
- [x] 5.2 Archive the change (sync deltas into `bubble-state-management` and `discovery-bubble-cache` canonical specs)
