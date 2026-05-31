## Context

The Discover tab (`src/routes/discovery/`) renders a Matter.js physics canvas of artist bubbles. `BubbleManager.loadInitialArtists()` seeds the field differently depending on follow state: a brand-new user gets the global Top 50 (`listTop(country, '', 50)`), while a user who already follows artists gets a similar-artist mix from random seeds. After load, tapping a bubble follows the artist and `onNeedMoreBubbles()` appends similar artists (with FIFO eviction at the 50-bubble cap); the genre chips can also swap the whole pool. There is no affordance to return to a clean baseline.

Separately, `src/styles/tokens.css` defines a utopia.fyi fluid type scale. Reverse-engineering the ratios (min 1.2 / max 1.25) shows every step sits on the modular curve **except** `--step--2`, which was hand-shrunk to `clamp(0.625rem, …, 0.7rem)` (10–11.2px) — below both the curve's predicted value (~11.1–12.8px) and the ~12px legibility floor. The discovery genre chips and ~22 other call sites consume this token.

## Goals / Non-Goals

**Goals:**
- Give users a one-tap way to return the bubble field to a stable, predictable baseline (global Top 50).
- Place the control where it reads as part of the bubble-field control strip, not as an unrelated chrome element.
- Lift the app-wide visible font floor to a legible size by moving most text to `--step--1`, while keeping genuinely compact UI compact.

**Non-Goals:**
- No change to the follow-seeded `loadInitialArtists()` path used on page load.
- No regeneration of the full utopia type scale; only the `--step--2` floor moves.
- No proto/backend/BSR work. No new RPCs — reset reuses `ArtistService` `listTop`.

## Decisions

### D1 — Reset target = global Top 50, not re-run of initial load
Reset always calls `listTop(country, '', 50)`, ignoring follows. **Alternative considered:** re-running `loadInitialArtists()` (which for a returning user yields a *different random* similar-artist mix each press). Rejected: a "reset" that produces non-deterministic output every time doesn't read as a reset. The global Top 50 is a stable anchor the user can always fall back to.

### D2 — Reset orchestrates existing machinery
Reset composes already-present operations rather than introducing new physics logic: clear `genre.activeTag`, `pool.clearSeenSets()` + `trackAllSeen(followed)`, fetch Top 50, dedup against followed, `pool.replace(...)`, and `dnaOrbCanvas.reloadBubbles(...)`. This mirrors the existing genre-deselect path (`GenreFilterController.reloadByCountry`), so the reset method lives naturally beside it.

### D3 — Control placement: sticky leading chip in the genre row
The reset button is an icon-only (⟳) control pinned as the **leading** item of `fieldset.genre-chips`, using `position: sticky` so it remains visible while chips scroll. **Alternatives considered:** (a) a FAB over the canvas — rejected because the canvas is an interactive physics surface and a persistent FAB competes with floating tappable bubbles and the bottom-nav; (b) a header icon next to help — rejected for poor thumb reach and weak semantic link to the bubbles. Reset is semantically a sibling of genre filtering (both swap the pool), so the chip row is the correct home.

### D4 — Font: raise `--step--2` floor to 11px (min-only)
`--step--2` becomes `clamp(0.6875rem, calc(0.6rem + 0.13vi), 0.7rem)`. 11px ≈ 16 ÷ 1.2², so the min end lands back on the modular curve. The max end stays at 0.7rem deliberately — the two surviving consumers are compact and should not grow on wide screens. **Alternative considered:** full curve restore to `clamp(0.6875rem, …, 0.8rem)` (12.8px max) — rejected because it would enlarge the only remaining `--step--2` consumers without benefit.

### D5 — Quarantine `--step--2` to two compact consumers
All `--step--2` usages migrate to `--step--1` **except** `bottom-nav-bar` and `.hype-col-header` (incl. its `& small`). This makes the app-wide visible floor `--step--1` (on-curve, 13.3–16px) and turns `--step--2` from a scale-wide anomaly into a documented CUBE "Exception" for two intentionally-tight components — a net gain in type-scale purity.

## Risks / Trade-offs

- **Reset confused with replenishment** → Distinct icon (⟳) and aria-label; reset replaces the whole pool whereas tap-replenishment appends. Behaviorally unambiguous.
- **Sticky chip overlaps first genre chip on scroll** → Background mask / matching surface behind the sticky button so chips scroll cleanly underneath; verify on narrow viewports.
- **Font bump enlarges dense UI** → Only ~2px; QA bottom-nav labels and the my-artists hype table specifically. The two compact spots are explicitly excluded.
- **Top-50 reset costs an API call** → Same `listTop` already used on load and genre filtering; in-memory cached client. Negligible.

## Migration Plan

Frontend-only, no data or schema migration. Ship via standard frontend PR → merge → dev → prod release (GH Release retag → cloud-provisioning prod pin bump). Rollback = revert the PR; tokens and discovery route are self-contained. Validate with `make lint` and visual QA before merge.

## Open Questions

None — placement (sticky leading chip), icon style (icon-only), reset target (global Top 50), and font scope (min-only, two exclusions) are all resolved.
