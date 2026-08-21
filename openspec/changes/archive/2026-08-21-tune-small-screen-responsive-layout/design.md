## Context

See `proposal.md — Why` for motivation.

Five files require changes, spanning two different control layers:
- **CSS layer** (`discovery-route.css`, `page-header.css`, `coach-mark.css`): padding and sizing adjustments.
- **Canvas/JS layer** (`dna-orb-canvas.ts`, `stage-effects.ts`): bubble count cap and orb radius cap driven by canvas dimensions, which are already tracked via an existing `ResizeObserver` + `resize()` hook.

The `bubble-area` container already declares `container-type: size`, but this is irrelevant to the JS-driven canvas — container queries cannot control TypeScript logic.

## Goals / Non-Goals

**Goals:**
- Reduce vertical UI chrome on screens ≤ 700px tall (search bar, page header).
- Cap rendered bubble count and orb radius when canvas width < 390px.
- Fix coach-mark tooltip overflow on 320px-wide devices.
- Keep all changes frontend-only with no data or API impact.

**Non-Goals:**
- Landscape orientation support (separate concern).
- Tablet or desktop layout changes.
- Bubble pool fetch logic or artist data changes.
- Any changes to bubble size or label rendering.

## Decisions

### D1: `@media (height <= 700px)` for CSS vertical compression

**Decision**: Use `@media (height <= 700px)` in `discovery-route.css` and `page-header.css` to tighten `padding-block` on short screens.

**Why not `@container (max-block-size: ...)`**: `bubble-area` has `container-type: size`, but `search-bar` and `page-header` are siblings/ancestors of `bubble-area` — not descendants — so they cannot be queried from inside it. A `@container` approach would require adding a new wrapper container above both, adding complexity for no benefit.

**Why `height` not `width`**: The constraint on iPhone SE is vertical. The screen is 375px wide (enough for the layout) but 667px tall (limiting bubble-area height). Height-based media queries target the actual constraint.

**Threshold choice (700px)**: iPhone SE is 667px; iPhone 14 is 844px. 700px captures all "short" phones without affecting standard-height devices.

### D2: Bubble count and orb radius derived from `canvasWidth` inside `resize()`

**Decision**: Read `canvasWidth` (already computed in `resize()`) and derive a `displayLimit` and `effectiveMaxRadius` based on the 390px threshold. Pass these to the physics initializer and `getStageParams`.

**Why not CSS custom properties or JS `matchMedia`**: The physics engine and orb renderer work in canvas pixel space, not CSS layout space. Using the already-available `rect.width` from `getBoundingClientRect()` in `resize()` is the simplest and most direct path — no extra subscriptions.

**Why 390px threshold**: iPhone SE is 375px CSS pixels; most "standard" phones start at 390px (iPhone 14). This naturally separates small-form-factor devices from the mainstream.

**Why reduce count, not size**: Reducing bubble radius below ~30px degrades label readability. Reducing count while keeping radius intact preserves the visual quality of each bubble.

### D3: Coach-mark uses `min()` instead of a media query

**Decision**: Change `max-inline-size: 320px` to `max-inline-size: min(320px, calc(100dvw - 2 * var(--space-s)))` in `coach-mark.css`.

**Why not a media query**: The tooltip is a floating component that could appear anywhere on any route. A single `min()` value self-adapts to any viewport without needing a separate `@media` block.

## Risks / Trade-offs

- **Bubble count threshold is a hard cutoff at 390px**: A device that is 389px wide will show 30 bubbles; one that is 390px will show 50. This may be noticeable if a user rotates their device. Acceptable because the transition happens at landscape rotation, which is already an edge case for this UI.
- **`@media (height <= 700px)` is viewport height, not available canvas height**: The page header and search bar shrink based on viewport height, not on how tall the bubble-area actually is. In practice these track closely enough on mobile.

## Migration Plan

Frontend-only change. Deploy as a standard frontend release. No data migrations or feature flags required. Rollback is a normal frontend rollback.
