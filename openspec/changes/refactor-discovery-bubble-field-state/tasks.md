## 1. Phase 0 — Stop-the-bleed: physics render parity (independently shippable)

- [x] 1.1 `bubble-physics.ts`: add `reconcile(target: Artist[])` that diffs `bubbleMap` vs target (keep matching ids, fade/remove ids not in target, add ids not present)
- [x] 1.2 `bubble-physics.ts`: stop counting fading-out bodies against capacity when adding; remove the silent `break` in `addBubbles` cap path (replace with a logged hard safety ceiling that never silently drops a target member)
- [x] 1.3 `dna-orb-canvas.ts`: route `artistsChanged` through `physics.reconcile(newVal)` instead of the fade-out + `revealGhostBubbles` + `addBubbles` sequence for the real-artist path
- [x] 1.4 Unit tests: reconcile converges body set to target; background-refresh transition ends with body count == field count (covers `bubble-state-management` "Background refresh preserves render parity" + "Physics never silently drops a target member"). Also added a revive-on-re-add regression test (mid-fade target member re-added within the fade window) per #514 review.
- [x] 1.5 `make check` green
- [x] 1.6 Frontend PR (#514) → CI green → merge → Release (v1.39.2) → prod roll (CP pin 850104b). Prod-verified via the live Aurelia VM: rendered physics bodies == UNIQUE pool artists, `inPoolButNotRendered=0`, no collapse. NOTE: raw `pool.length` > rendered because the pool still holds duplicates (seed-similar top-up dedup gap) — physics dedupes by id so the field is visually correct; the pool-level dedup is fixed by Phase 1 task 2.2 (invariants applied once). Also shipped deps PR #516 (dompurify ^3.4.13 override) to clear the repo-wide Security Audit gate.

## 2. Phase 1 — Single source of truth (DiscoveryFieldStore)

- [ ] 2.1 Add `DiscoveryFieldStore` (DI app-singleton) owning `field: Artist[]`, with a single `setField`/`update` path that applies invariants (exclude-followed + dedup + 50-cap) exactly once
- [ ] 2.2 Move follow-exclusion, dedup, and cap out of `discovery-route.ts` `loading()`, `bubble-manager.ts`, and `genre-filter-controller.ts` into the field store's single boundary (covers `bubble-state-management` "Bubble invariants are applied once at the field boundary")
- [ ] 2.3 Reduce `BubblePool` to a pure dedup/cap helper (or fold into the field store); remove its role as a second authoritative membership store
- [ ] 2.4 Aurelia observation contract: field store emits an immutable snapshot (new array reference) on each update; wire the canvas to consume it so `artistsChanged` fires deterministically; wrap multi-step updates in `batch()`
- [ ] 2.5 Separate lifecycle: `loading()` only requests a field update; canvas initializes from the store snapshot in `attached()` and reconciles on change; unsubscribe in `detaching`/`unbinding`
- [ ] 2.6 Unit tests: invariants applied once (no double-filter downstream); field↔physics parity on add/remove/evict (covers `bubble-state-management` SSoT scenarios)
- [ ] 2.7 `make check` green
- [ ] 2.8 Frontend PR → CI green → merge → Release → prod roll

## 3. Phase 2 — Preserve the in-session field on re-entry

- [ ] 3.1 Field store: on re-entry, if the cached field is fresh (within TTL) reuse it and apply a non-destructive delta (remove newly-followed, top-up only below the display floor); no wholesale `replace()`
- [ ] 3.2 Field store: stale (TTL-expired) re-entry falls back to a full cold-style reload that still converges within capacity with render parity
- [ ] 3.3 Remove the unconditional wholesale background `pool.replace()` on re-entry from `discovery-route.ts` / `bubble-manager.ts`
- [ ] 3.4 Unit tests: fresh re-entry reuses field and does not shrink below prior count (minus follows); follow-while-away removes only the followed and tops up to floor (covers `discovery-bubble-cache` re-entry-preservation scenarios)
- [ ] 3.5 `make check` green
- [ ] 3.6 Frontend PR → CI green → merge → Release → prod roll; verify in prod: navigate away and back keeps the field (no collapse to a few bubbles), following an artist then re-entering removes only that artist

## 4. Phase 3 — Cleanup: collapse caches and duplicated logic

- [ ] 4.1 Remove `ArtistStore.lastBubbles` (`peekBubbles`/`setBubbles`); the single bubble-field cache lives in `DiscoveryFieldStore` derived from the SWR `listTop` results (covers `discovery-bubble-cache` single-cache requirement)
- [ ] 4.2 Remove any remaining duplicated dedup/cap/followed-filter call sites; confirm the physics layer applies no policy
- [ ] 4.3 (Optional) Rename `ArtistStore` to a repository role to reflect raw-RPC-cache-only responsibility
- [ ] 4.4 `make check` green
- [ ] 4.5 Frontend PR → CI green → merge → Release → prod roll

## 5. Close-out

- [ ] 5.1 Verify all delta spec scenarios are satisfied by the shipped implementation (render parity, invariants-once, re-entry preservation, single cache)
- [ ] 5.2 Archive the change (sync deltas into `bubble-state-management` and `discovery-bubble-cache` canonical specs)
