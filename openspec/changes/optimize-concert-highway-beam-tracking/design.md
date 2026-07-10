## Context

`<concert-highway>` renders laser beams (one per matched event card) as `position: fixed` overlay triangles whose height and `clip-path` apex track each card's viewport position. The tracking runs in `updateBeamPositions()`, scheduled by a passive scroll listener via `requestAnimationFrame`:

```
for (const beamEl of beamEls) {
  const card = this.element.querySelector(`[data-beam-index="${idx}"]`) // per-frame, per-beam DOM query
  const rect = card.getBoundingClientRect()                            // READ  (layout)
  beamEl.style.setProperty('--beam-h', `${rect.bottom}px`)             // WRITE
  beamEl.style.setProperty('--beam-top-pct', ...)                      // WRITE
}
```

Two implementation costs, both on the dashboard + Welcome-preview hot path:

1. **Per-frame `querySelector`** — N matched beams × every scroll frame, re-querying the same stable card elements.
2. **Read/write interleave** — `getBoundingClientRect` (read) and `setProperty` (write) alternate within one loop. Beams live in a `position: fixed` overlay (a separate layout subtree), so the practical forced-reflow risk is bounded, but the shape is the canonical layout-thrash anti-pattern and trivially avoidable.

An exploration confirmed the beams were **never** driven by CSS scroll-driven animations (`animation-timeline` has no history in `live-highway`), and the `@keyframes beam-descend` in `event-card.css` is dead decorative code from the festival-spotlight change, never referenced.

## Goals / Non-Goals

**Goals:**
- Remove the per-frame `querySelector` by caching a beam-anchor → card `HTMLElement` map, rebuilt only when `dateGroups` / the beam index map change (the same triggers that rebuild `laserBeams`).
- Split each rAF update into a read phase (collect all `getBoundingClientRect` results) followed by a write phase (apply all `setProperty` writes) — no interleave.
- Preserve pixel-identical beam output and the existing `requestAnimationFrame` cadence.
- Remove the dead `@keyframes beam-descend`.

**Non-Goals:**
- Replacing the JS tracking with CSS scroll-driven animations (`animation-timeline: view()`). Deferred: needs a geometry redesign (the non-linear `--beam-top-pct = rect.top/rect.bottom` resists linear keyframe interpolation), dynamic per-card `view-timeline-name` + `timeline-scope`, and a mandatory `@supports` fallback for iOS/Safari (no browser-support policy is declared, so scroll-driven animations are not assumed Baseline). Benefit is also unmeasured.
- Any change to beam appearance, `clip-path` geometry, hue, or the fixed-overlay containing-block rule.

## Decisions

**D1 — Cache the anchor→element map, keyed by beam-anchor index.**
Build a `Map<number, HTMLElement>` (or an array indexed by anchor) alongside `laserBeams`/`beamIndexMap`, populated by querying `[data-beam-index]` once per rebuild. `updateBeamPositions` reads from the cache instead of querying per frame. Rationale: the card elements are stable between rebuilds; the existing `buildBeamIndexMap()` already runs on exactly the change events that would invalidate the cache, so it is the natural rebuild point. Alternative considered: `ref`/binding-collected element list — rejected as more invasive to the template for no gain over a single post-render query.
Cache-miss safety: a stale/missing entry (element not yet in DOM) is skipped for that frame exactly as the current `if (!card) continue` does.

**D2 — Two-phase read-then-write per rAF.**
Iterate once to collect `{ beamEl, rect | offscreen }` into a local array (reads only), then iterate the collected results to apply `--beam-h` / `--beam-top-pct` (writes only). Rationale: guarantees all layout reads complete before any style mutation, eliminating any read-after-write forced reflow regardless of how the browser scopes invalidation. Alternative: rely on the fixed-overlay subtree isolation and leave the interleave — rejected; the batched form is strictly safer and the same line count.

**D3 — Encode the invariant as a spec requirement, not just a code comment.**
The `concert-highway-ce` "Laser beam effects" scenario gains an efficiency clause (cached resolution + batched read-before-write). Rationale: prevents a future edit from reintroducing the per-frame query / interleave; the behavior itself is unchanged so this is a MODIFIED scenario, not new behavior.

## Risks / Trade-offs

- **[Cache goes stale if cards re-render without a rebuild trigger]** → The cache is rebuilt in the same `buildBeamIndexMap()` path that already reruns on `dateGroups` / attach; a missing entry degrades gracefully (skip that beam for the frame, next rebuild repairs it) exactly as today's null-guard. No new failure mode.
- **[Behavior drift vs. current visuals]** → Output must be byte-for-byte identical; guarded by the existing `concert-highway.spec.ts` plus a manual scroll check. Reads and writes compute the same values, only reordered.
- **[Perf win is modest / unmeasured]** → Accepted. This is low-risk hygiene (fewer queries, no interleave, dead-code removal), not a promised metric. The full CSS rewrite that could yield a larger win is explicitly deferred pending measurement and an iOS fallback decision.

## Migration Plan

Pure frontend refactor, no data or API migration. Deploy path: merge to `frontend` main → frontend Release (retag → prod AR → automated prod pin-bump → ArgoCD) onto the healthy v1.24.0 baseline. Rollback: revert the frontend PR (or re-pin the prior release); no state to unwind.

## Open Questions

- Should beam-update cost be measured (DevTools Performance on a beam-dense dashboard) to decide whether the deferred CSS scroll-driven redesign is ever worth pursuing? Out of scope here; noted for a follow-up.
