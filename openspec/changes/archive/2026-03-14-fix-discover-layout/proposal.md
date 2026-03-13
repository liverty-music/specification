## Why

The Discover page layout is structurally broken: the `dna-orb-canvas` (position: absolute) resolves its containing block to `.discover-layout` instead of `.bubble-area`, causing the canvas to overlay the search bar and genre chips. This is a fundamental CSS architecture issue — the containing block chain, container query setup, and state management pattern all need correction to align with CUBE CSS methodology.

## What Changes

- Fix the CSS containing block chain so the canvas is scoped to `.bubble-area`, not the entire page
- Convert `.bubble-area` to a proper container query context (`container-type: size`) for both-axis responsiveness
- ~~Replace the starfield `::before` pseudo-element from `position: absolute` to CSS Grid single-cell stacking (eliminating the need for `position: relative` on `.discover-layout`)~~ (reverted — grid stacking broke CSS Grid auto-placement)
- Migrate browse/search mode toggling from CSS class (`.hidden`) to `data-state` attribute, following CUBE CSS exception patterns
- Reposition `.orb-label` using container-relative units (`cqb`) instead of a fixed `10rem` magic number

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this is a CSS implementation fix, not a requirement change)

## Impact

- **frontend** `src/routes/discover/discover-page.css` — Primary change: grid structure, containing block, container query, state selectors
- **frontend** `src/routes/discover/discover-page.html` — Replace class-based `.hidden` toggling with `data-state` attribute binding
- **frontend** `src/components/dna-orb/dna-orb-canvas.css` — No changes expected (containing block fix resolves the issue upstream)
- **frontend** `src/components/dna-orb/orb-renderer.ts` — No changes expected (canvas dimensions will auto-correct)
- **frontend** `src/components/dna-orb/bubble-physics.ts` — No changes expected (physics boundaries will auto-correct)
