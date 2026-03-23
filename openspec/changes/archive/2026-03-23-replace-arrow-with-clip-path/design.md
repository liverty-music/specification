## Context

The coach-mark component uses two SVG divs (`.coach-arrow-above`, `.coach-arrow-below`) with hardcoded curving paths. The current `anchor()` positioning centers the arrow box on the target, but the SVG curve always goes left, making the arrow point away from the target in many layouts. The community best practice (css-tip.com, Frontend Masters) uses `::before` pseudo-elements with `clip-path: polygon()` and `margin: inherit` to create arrows that automatically orient toward the anchor.

## Goals / Non-Goals

**Goals:**
- Arrow always points toward the target regardless of tooltip position
- Pure CSS solution — no JS for arrow direction
- Symmetric arrow shape that works with `flip-block`
- Reduce HTML complexity (remove 2 SVG container divs)

**Non-Goals:**
- Preserving the handwritten/curved arrow aesthetic (accepting triangular arrow)
- Supporting left/right tooltip placement (only block-end/block-start needed)

## Decisions

### 1. Use `::before` pseudo-element instead of SVG divs

**Chosen:** `::before` on `.coach-mark-tooltip` with `clip-path: polygon()`
**Alternatives considered:**
- Symmetric SVG: still needs two divs and display toggling
- `::after`: no semantic difference, `::before` is conventional for arrows

**Rationale:** Eliminates HTML elements, works natively with `position-try-fallbacks` via `margin: inherit`, and is the established community pattern.

### 2. Arrow shape via `clip-path: polygon()`

**Chosen:** Triangular polygon pointing upward by default, masked by margin on flip

```css
.coach-mark-tooltip::before {
  content: "";
  position: fixed;
  width: var(--arrow-size);
  aspect-ratio: 1;
  background: inherit;
  left: calc(anchor(--coach-target center) - var(--arrow-size) / 2);
  top: calc(anchor(--coach-tooltip top) - var(--arrow-gap));
  bottom: calc(anchor(--coach-tooltip bottom) - var(--arrow-gap));
  margin: inherit;
  clip-path: polygon(
    50% 0,
    100% var(--arrow-gap),
    100% calc(100% - var(--arrow-gap)),
    50% 100%,
    0 calc(100% - var(--arrow-gap)),
    0 var(--arrow-gap)
  );
  z-index: -1;
}
```

**How flip works:** The `margin: inherit` causes the pseudo-element to inherit the tooltip's margin (set by `position-area`). When `flip-block` activates, the margin flips, hiding the top or bottom half of the diamond-shaped clip-path, making only the correct arrow direction visible.

### 3. Anchor the tooltip with `anchor-name: --coach-tooltip`

The tooltip needs its own anchor name so the `::before` can reference both `--coach-target` (for horizontal centering) and `--coach-tooltip` (for vertical extent).

### 4. Remove `@container anchored` arrow toggling

The current `@container anchored (fallback: flip-block)` rules that toggle `.coach-arrow-above`/`.coach-arrow-below` visibility become unnecessary. The `margin: inherit` pattern handles this automatically.

## Risks / Trade-offs

- **Visual change:** Triangular arrow looks different from the handwritten SVG curve. Acceptable per user decision.
- **`clip-path` browser support:** Widely supported (Baseline 2023). No concern.
- **`anchor()` in `::before`:** The pseudo-element uses `position: fixed` to escape the tooltip's coordinate space and reference anchors directly. Verified working in current Chrome.
- **Animation:** The current stroke-dasharray draw animation on the SVG will be lost. Could add a fade-in or scale animation on the `::before` instead.
