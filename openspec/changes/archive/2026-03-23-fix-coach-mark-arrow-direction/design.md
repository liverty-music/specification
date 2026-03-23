## Context

The coach mark component uses CSS Anchor Positioning to place a tooltip with a hand-drawn arrow below (or above) the target element. Currently, the arrow SVG always curves to the upper-left, regardless of the target's horizontal position. When the target is on the right side of the screen (common for concert cards), the arrow visually points away from the target.

The existing `onboarding-spotlight` spec already requires `position-try-fallbacks: flip-block, flip-inline`, but the implementation only uses `flip-block`. The `position-area` is set to `block-end` (horizontally centered), which gives `flip-inline` nothing to flip.

## Goals / Non-Goals

**Goals:**
- Arrow visually curves toward the target in all 4 quadrants (above/below x left/right)
- Pure CSS solution — no JavaScript for arrow direction logic
- Leverage CSS Anchor Positioning L2 anchored container queries (already in use for vertical flipping)

**Non-Goals:**
- Diagonal or arbitrary-angle arrow support (4 cardinal directions suffice)
- Changing the hand-drawn SVG art style
- Adding new arrow SVG variants (reuse existing paths via CSS `transform`)

## Decisions

### Decision 1: `position-area: block-end inline-start` with `flip-inline`

**Choice**: Change `position-area` from `block-end` to `block-end inline-start`.

**Why**: `position-area: block-end` centers the tooltip below the target — there is no inline direction to flip. By biasing the tooltip to `inline-start` (left in LTR), the browser can flip to `inline-end` (right) when viewport space requires it. This gives the anchored container query a `flip-inline` state to detect.

**Alternative considered**: Keep `block-end` and compute direction in JavaScript. Rejected because the codebase already uses anchored container queries for the vertical case, and consistency favors a pure-CSS approach.

**Alternative considered**: Use named `@position-try` rules instead of `flip-inline` tactic. Rejected because `@container anchored (fallback: ...)` can only match tactic keywords (`flip-block`, `flip-inline`), not named rules.

### Decision 2: `transform: scaleX(-1)` for horizontal mirroring

**Choice**: Mirror the existing arrow SVGs using CSS `transform: scaleX(-1)` rather than creating new SVG path variants.

**Why**: The current arrow paths curve from bottom-center to upper-left. Mirroring via `scaleX(-1)` produces a right-curving arrow with zero HTML changes. This keeps the hand-drawn aesthetic consistent and avoids maintaining duplicate SVG paths.

### Decision 3: 4-state arrow toggle via anchored container queries

**Choice**: Expand from 2 states (above/below) to 4 states using combinations of `flip-block` and `flip-inline`:

```
                    No inline flip         flip-inline
                ┌────────────────────┬────────────────────┐
 No block flip  │ below-left         │ below-right        │
 (block-end)    │ arrow-above        │ arrow-above        │
                │ scaleX(-1) (→右上)  │ scaleX(1) (←左上)  │
                ├────────────────────┼────────────────────┤
 flip-block     │ above-left         │ above-right        │
 (block-start)  │ arrow-below        │ arrow-below        │
                │ scaleX(-1) (→右下)  │ scaleX(1) (←左下)  │
                └────────────────────┴────────────────────┘
```

CSS implementation pattern:
```css
position-try-fallbacks: flip-block, flip-inline, flip-block flip-inline;

/* Default (below-left): arrow curves right toward target */
.coach-arrow-above  { display: block;  transform: scaleX(-1); }
.coach-arrow-below  { display: none; }

@container anchored (fallback: flip-inline) {
  /* below-right: arrow curves left (SVG default) */
  .coach-arrow-above  { transform: scaleX(1); }
}

@container anchored (fallback: flip-block) {
  /* above-left: swap to below arrow, curves right */
  .coach-arrow-above  { display: none; }
  .coach-arrow-below  { display: block; transform: scaleX(-1); }
}

@container anchored (fallback: flip-block flip-inline) {
  /* above-right: swap to below arrow, curves left */
  .coach-arrow-above  { display: none; }
  .coach-arrow-below  { display: block; transform: scaleX(1); }
}
```

### Decision 4: Default `scaleX(-1)` for `inline-start` bias

**Choice**: In the default state (`inline-start` = tooltip left of target center), the arrow is mirrored (`scaleX(-1)`) so it curves to the RIGHT — toward the target which is to the right of the tooltip.

**Why**: The SVG paths natively curve to the left. With `inline-start` positioning, the target is generally to the right of the tooltip, so mirroring makes the arrow point toward the target. When `flip-inline` triggers (tooltip moves to the right), the original left-curving SVG correctly points left toward the target.

## Risks / Trade-offs

- **[Tooltip position shift]** Changing from `block-end` (centered) to `block-end inline-start` (left-biased) moves the tooltip slightly. → **Mitigation**: The tooltip is `max-inline-size: 320px` on mobile viewports where the difference is minimal. The arrow pointing toward the target improves UX more than the slight position change detracts.

- **[Browser support for anchored container queries]** `@container anchored (fallback: flip-inline)` is CSS Anchor Positioning L2. → **Mitigation**: The codebase already uses `@container anchored (fallback: flip-block)` without a polyfill, so browser support baseline is already established. Graceful degradation: if the query is unsupported, the arrow stays in its default mirrored direction (better than current always-left behavior).

- **[`flip-inline` may not always trigger]** The browser only flips inline when the tooltip would overflow the viewport. If both sides have space, it stays at `inline-start`. → **Mitigation**: On mobile viewports (primary target), concert cards are typically right-aligned, so the tooltip at `inline-start` (left of target) will often have the target to its right — the mirrored arrow correctly points right. The flip triggers when targets are on the left side.
