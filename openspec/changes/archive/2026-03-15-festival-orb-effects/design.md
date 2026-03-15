## Context

The DNA Orb on the Discover page uses Canvas 2D with Matter.js physics. The current visual pipeline renders: bubbles → absorption animations → orb, all in a single `render()` method in `dna-orb-canvas.ts`. The orb is a fixed 70px radius glass sphere with 60 internal particles, rendered by `orb-renderer.ts` (200 lines). Visual intensity is driven by a single `orbIntensity` scalar (followCount/20) combined with a diminishing-returns `baseIntensity` curve. Both values saturate early — by 6 follows the orb is visually maxed out with nowhere to go.

The bubble area is bounded by a Matter.js static wall at `canvasHeight - 160` (hardcoded `orbZoneHeight`). The "MUSIC DNA · N" label is a DOM element positioned via CSS over the canvas.

## Goals / Non-Goals

**Goals:**
- Each follow produces a visibly distinct escalation in visual effects (festival stage metaphor)
- Orb grows in size, pushing the bubble play area upward naturally
- New effect layers (orbitals, rays, shockwave, comet trail, ground glow) are added progressively
- `stage-effects.ts` encapsulates all stage-level parameter calculation as pure functions, fully unit-testable
- Existing FPS monitoring and quality scaling continues to work, degrading new effects gracefully

**Non-Goals:**
- Applying festival aesthetic to other pages (dashboard, my-artists) — separate change
- WebGL/shader-based rendering — stay on Canvas 2D
- Sound effects or haptic feedback
- Changing the bubble physics behavior (gravity, restitution, etc.)

## Decisions

### 1. Separate `stage-effects.ts` for parameter calculation

**Decision**: Extract all follow-count → visual-parameter mapping into a pure module `stage-effects.ts`.

**Rationale**: The escalation system has ~15 parameters that change per follow. Keeping the calculation separate from rendering means: (a) unit tests cover the parameter curve without needing Canvas mocks, (b) future pages that want festival-style effects can import the same module, (c) tuning is localized to one file.

**Alternative considered**: Inline everything in `orb-renderer.ts`. Rejected because it would push the file to ~450 lines with interleaved calculation and draw calls, making tuning harder.

**Interface**:
```typescript
interface StageParams {
  level: number              // 0-based stage level (= followCount, uncapped)
  orbRadius: number          // 60 → 120 (asymptotic)
  breathAmplitude: number    // 0 → 0.05
  breathSpeed: number        // 1.5 → 3.0
  orbitalCount: number       // 0 → 12
  orbitalSpeedMultiplier: number
  lightRayCount: number      // 0 → 6
  lightRayAlpha: number      // 0 → 0.15
  lightRayRotationSpeed: number
  groundGlowAlpha: number    // 0 → 0.2
  shockwaveEnabled: boolean
  cometTrailEnabled: boolean
  glowAlpha: number          // outer glow alpha
  particleVisibilityRatio: number // 0.1 → 1.0
}

function getStageParams(followCount: number): StageParams
```

### 2. Orb radius growth formula

**Decision**: `orbRadius = min(120, 60 + followCount * 8)` for follows 1-6, then logarithmic growth: `60 + 48 + log2(followCount - 5) * 8` for 7+.

**Rationale**: Linear growth (8px/follow) gives immediate visible feedback for the first 6 follows (the tutorial target is 3). Logarithmic tail prevents the orb from consuming the entire canvas while still rewarding continued follows.

**Alternative considered**: Pure logarithmic from the start. Rejected because the initial follows need dramatic size jumps to feel rewarding.

### 3. Dynamic Matter.js wall repositioning

**Decision**: Add `updateOrbZone(radius: number)` to `BubblePhysics`. When the orb radius changes, the bottom wall is repositioned to `canvasHeight - (radius * 2 + 20)`, giving the orb its radius plus 20px breathing room above the wall.

**Rationale**: Matter.js supports repositioning static bodies via `Body.setPosition()`. This is the simplest approach — no wall recreation needed.

**Alternative considered**: Recreating walls on each follow. Rejected because `setPosition` on an existing static body is cheaper and avoids re-adding to the composite.

### 4. Render layer ordering

**Decision**: Extend the render pipeline to 7 layers:

```
0. Ground glow          (below everything)
1. Light rays           (additive blend, behind bubbles)
2. Bubbles              (existing)
3. Comet trails         (behind absorption bubble, ahead of field bubbles)
4. Absorption animations (existing)
5. Orb body             (existing, with breathing pulse)
6. Orbital particles    (foreground, on top of orb)
7. Shockwave rings      (foreground, expanding outward)
```

**Rationale**: Ground glow and light rays go behind bubbles to create depth. Orbitals and shockwaves go on top of the orb because they're foreground spectacle. Comet trails are behind the absorption bubble body so the artist name remains readable.

### 5. Additive blending for light effects

**Decision**: Use `globalCompositeOperation = 'screen'` for light rays and ground glow, wrapped in `ctx.save()/restore()` to avoid affecting other layers.

**Rationale**: Additive blending makes overlapping lights brighter, matching real stage lighting. `'screen'` is well-supported and GPU-accelerated on all target browsers.

### 6. Comet trail implementation

**Decision**: Store the last 12 frame positions in a circular buffer on each `AbsorptionAnimation`. Render as segmented lines with decreasing width (4px → 1px) and opacity (0.7 → 0.05) from head to tail, colored with the artist's hue.

**Rationale**: A circular buffer avoids allocations. 12 points at 60fps covers ~200ms of trail, long enough to be visible on the curved bezier path. Line segments are cheaper than bezier curves for the trail itself.

**Alternative considered**: Render trail as a series of circles (dots). Rejected because connected lines give a smoother comet appearance.

### 7. Shockwave ring lifecycle

**Decision**: Shockwave rings are stored as a small array (`maxConcurrent = 3`) in `OrbRenderer`. Each ring has: `radius` (starts at orbRadius, expands to orbRadius × 3), `alpha` (0.6 → 0), `lineWidth` (3 → 0.5), `hue`, and progresses over 800ms. Completed rings are recycled.

**Rationale**: Object pooling (max 3) avoids GC. 800ms duration is long enough to be seen but short enough to not linger. The ring inherits the absorbed artist's hue for color continuity.

### 8. Orbital particle management

**Decision**: Pre-allocate orbital slots (max 12) in `OrbRenderer`. Each orbital has: `angle`, `orbitalRadius` (1.3-1.8 × orbRadius), `speed`, `size` (2-5px), `hue`. Visible count is `stageParams.orbitalCount`. Orbitals are rendered as small radial gradients (glow dots).

**Rationale**: Pre-allocation matches the existing pattern for inner particles. Max 12 keeps draw calls reasonable. Each orbital is 1 `arc()` + 1 small `radialGradient`, which is efficient.

### 9. Color palette accumulation

**Decision**: Maintain a `colorPalette: number[]` (max 20 hues) in `OrbRenderer`. Each `injectColor(hue)` call appends to the palette. Orbital particles and light rays sample colors from the palette, distributing them evenly.

**Rationale**: This naturally enriches the visual diversity as more artists are followed. The palette array is trivially cheap. Capping at 20 prevents unbounded growth while covering the full hue spectrum.

### 10. Unit test strategy

**Decision**: Test `stage-effects.ts` exhaustively with Vitest. Test key state transitions in `OrbRenderer` (shockwave lifecycle, color palette, orbital count changes). Do not test Canvas draw calls directly.

**Rationale**: `getStageParams()` is a pure function — ideal for unit tests. OrbRenderer state logic (palette, shockwave pool, orbital slots) can be tested by calling methods and asserting state, without needing a Canvas context. Asserting actual pixel output would require canvas mocking and provides little value.

**Test coverage targets**:
- `stage-effects.ts`: Every parameter at follow counts 0, 1, 3, 5, 6, 10, 20 (boundary values)
- `OrbRenderer`: shockwave spawn/complete lifecycle, color palette accumulation and cap, orbital count changes, breathing pulse state, `prefers-reduced-motion` behavior
- `AbsorptionAnimator`: comet trail point accumulation and circular buffer behavior

## Risks / Trade-offs

- **[Mobile performance with all effects active]** → Mitigated by existing FPS monitoring (`monitorPerformance`). When FPS drops below 40, reduce `orbitalCount` and `lightRayCount` via `qualityScale`. Ground glow and shockwave rings are single draw calls and negligible.

- **[Orb growth compresses bubble area]** → At max orb size (120px radius), the bottom wall sits at ~canvasHeight - 260, leaving roughly 60% of the canvas for bubbles on a typical mobile screen (800px viewport). With ~30 bubbles this is still comfortable. If it feels cramped, the growth ceiling can be tuned in `stage-effects.ts` without touching rendering code.

- **[Additive blending artifacts]** → `screen` blending on semi-transparent backgrounds can produce unexpected brightness. Mitigated by keeping light ray alpha low (max 0.15) and always wrapping in save/restore.

- **[Breaking existing spec assertions]** → The `artist-discovery-dna-orb-ui` spec has specific assertions about `baseIntensity` formula and fixed thresholds. These will be superseded by the updated spec. The delta spec must clearly mark which scenarios are replaced.
