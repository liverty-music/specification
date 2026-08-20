## Why

Small-screen mobile devices (iPhone SE and similar, 375px wide / 667px tall) render the Discovery page with overly dense artist bubbles and proportionally oversized UI chrome — the search bar, page header, and DNA Orb occupy a disproportionate share of the vertical space, leaving the bubble canvas cramped. The root cause is that bubble count, orb radius, and key UI padding values are all screen-size-agnostic constants.

## What Changes

- **Discovery search bar**: Reduce `padding-block` on short screens (`height ≤ 700px`) from `var(--space-2xs)` (8px) to `var(--space-3xs)` (4px), recovering ~8px of vertical space.
- **Page header**: Reduce `padding-block` on short screens, recovering ~8px of vertical space in the header row.
- **DNA Orb radius**: Cap `MAX_RADIUS` at ~70px (down from 90px) when canvas width is < 390px, reducing orb dominance on small screens.
- **Bubble count**: Cap the number of artist bubbles rendered in physics at ~30 when canvas width is < 390px (instead of the unconditional maximum of 50), reducing canvas area saturation while preserving visual richness.
- **Coach Mark tooltip**: Change `max-inline-size` from the fixed `320px` to `min(320px, calc(100dvw - 2 * var(--space-s)))` so the tooltip cannot overflow on 320px-wide devices.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Add a screen-size-aware constraint on the number of bubbles rendered and the DNA Orb radius. The existing requirement specifies "approximately 30 artist bubbles"; this change makes that bound formally responsive to canvas width.

## Impact

- **Frontend only**: `discovery-route.css`, `page-header.css`, `coach-mark.css`, `dna-orb-canvas.ts`, `stage-effects.ts`.
- No backend, protocol buffer, or infrastructure changes.
- No changes to pool fetch logic, follow state, or artist data; only the visual rendering layer is affected.
