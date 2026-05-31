## Why

On the Discover tab, following an artist spawns similar-artist bubbles and may apply a genre filter, so the bubble field steadily drifts away from its initial state with no way back to a clean starting point. Separately, the smallest type-scale token (`--step--2`) was hand-shrunk below the modular curve to 10px, rendering the genre chips (and ~22 other usages) below the practical legibility floor.

## What Changes

- Add a **Reset control** to the Discover tab that restores the bubble field to the **global Top 50** artists (independent of the user's follows), clearing any active genre filter and the accumulated similar-artist bubbles.
- The control is an **icon-only (⟳) button** at the leading edge of the genre row, a fixed sibling beside the horizontally-scrollable genre chips, so it stays visible while the chips scroll.
- Raise the type-scale minimum floor (`--step--2`) from **10px → 11px** (min-only), restoring min-end curve purity.
- Migrate the ~22 non-compact `--step--2` consumers to `--step--1` (13.3–16px), leaving `--step--2` as a documented exception used only by two intentionally-compact classes (`bottom-nav-bar`, `.hype-col-header`).

## Capabilities

### New Capabilities
<!-- None — all changes extend existing capabilities. -->

### Modified Capabilities
- `discover`: Add a Reset-to-Top-50 control to the Discover tab's genre-chips row, defining its placement, behavior, and accessibility.
- `bubble-state-management`: Add a reset operation that replaces the entire pool with the global Top 50, clears seen-sets and eviction history, and re-synchronizes physics state.
- `design-system`: Raise the type-scale minimum legibility floor (`--step--2` → 11px) and scope `--step--2` to compact-only usage, with all other text resting on `--step--1` or larger.

## Impact

- **Frontend only** (Aurelia 2 PWA). No proto, backend, or BSR changes.
- Discovery page: `src/routes/discovery/discovery-route.{html,ts,css}`, `bubble-manager.ts`, `genre-filter-controller.ts`.
- Design tokens: `src/styles/tokens.css` (`--step--2`).
- ~13 CSS files migrate `--step--2` → `--step--1` (discovery, artist-filter-bar, page-help, user-home-selector, concert-highway, event-card, event-detail-sheet, post-signup-dialog, inline-error, error-banner, tickets-route, settings-route, consent-route).
- Validation via `make lint` + visual QA of bottom-nav labels and the my-artists hype table.
