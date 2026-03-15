## Context

The DNA Orb in `src/components/dna-orb/` uses Canvas 2D to render a growing glass sphere with inner particles, orbital dots, light rays, shockwaves, and ground glow. All visual parameters are driven by `getStageParams(followCount)` in `stage-effects.ts`, which returns a `StageParams` object consumed by `OrbRenderer`.

Current state:
- Inner particles are small dots (1-3px) scattered via `Math.random()` — no trails, no fluid motion
- Light rays are monochrome triangles (max 6, alpha 0.15, fixed 0.15 rad width)
- Orbitals are small glow dots (2-5px, glow radius = size * 2)
- Full escalation takes 8+ follows; users typically follow 5-10 artists during onboarding
- The orb interior is mostly empty space at larger radii

All rendering uses `CanvasRenderingContext2D`. No WebGL, no external animation libraries beyond Matter.js (physics only). Performance target is 60fps on Pixel 7 class devices.

## Goals / Non-Goals

**Goals:**
- Make the follow action feel dramatically rewarding — every follow should produce visible, exciting change
- Reach full visual intensity at follow 5 (compressed from 8+)
- Create a "live concert stage" atmosphere through layered lighting effects
- Maintain 60fps on mobile at maximum effect intensity
- Respect `prefers-reduced-motion`

**Non-Goals:**
- WebGL migration — Canvas 2D is sufficient for the effect count
- Audio/haptic feedback — out of scope for this visual-only change
- Changing the bubble physics, absorption animation paths, or Matter.js integration
- Modifying the orb's max radius (stays at 120px) or growth formula shape

## Decisions

### 1. Vortex trails via position history buffer

**Decision**: Each `OrbParticle` gains a `trail: {x, y}[]` ring buffer (length 6). On each `update()`, the current position is pushed. `render()` draws a tapered `lineTo` path instead of a single `arc`.

**Why not a shader/blur approach**: Canvas 2D has no efficient motion blur. A trail buffer is O(n) memory and O(n) draw calls — both trivial at 60 particles × 6 trail points = 360 line segments.

**Why 6 trail points**: Enough to show a smooth curve at 60fps (~100ms of trail). More points increase visual noise without adding perceived fluidity.

### 2. Nebula as rotating radial gradients with screen compositing

**Decision**: Add 2-3 `createRadialGradient` calls inside the orb, each rotated at different speeds using `translate`/`rotate` transforms. Colors sampled from `colorPalette`. Composited with `globalCompositeOperation = 'screen'`.

**Why not pre-rendered textures**: Textures would need to change color dynamically as the palette grows. Runtime gradients are cheap at the orb's pixel area (~45,000 px² at max radius) and allow palette-reactive colors.

**Why screen compositing**: Additive blending makes overlapping nebula layers glow brighter at intersections — natural light behavior that enhances the "energy" feel.

### 3. Laser rays with per-ray linear gradients and randomized widths

**Decision**: Replace the single `fillStyle` color with a `createLinearGradient` from orb center to ray tip. Each ray gets a randomized `halfWidth` (0.08-0.25 rad) seeded at init. Some rays rotate counter-clockwise.

**Why gradient over flat fill**: A gradient fading to transparent at the tip eliminates the hard triangle edge, making rays look like actual light beams rather than colored wedges.

**Why counter-rotation**: A mix of CW/CCW rays creates visual complexity without increasing ray count. Two rays crossing paths catch the eye more than two rays moving in parallel.

### 4. Orbital comet tails via arc segments

**Decision**: Each orbital particle draws a trailing arc segment (30-45 degrees behind its current angle) with a gradient from full opacity to transparent. Size increased to 4-8px with glow radius = size × 4.

**Why arc, not trail buffer**: Orbitals follow a circular path, so the trail is always a perfect arc. Drawing an arc segment is a single `ctx.arc()` call — cheaper than a multi-point trail.

### 5. Strobe as single-frame overlay + staggered shockwaves

**Decision**: On `pulse()`, draw a full-canvas `fillRect` with `rgba(255,255,255,0.15)` for exactly 1 frame. Simultaneously fire 2-3 shockwaves at 50ms stagger (using the existing `ShockwaveRing` pool, increased from 3 to 5 slots). Spike all light ray alpha to 0.8 for 200ms.

**Why 0.15 alpha**: Higher values (0.3+) cause discomfort on OLED screens in dark rooms. 0.15 is perceptible as a flash without being harsh. Reduced-motion users skip the flash entirely.

### 6. Beat sync via shared sine modulator

**Decision**: Add a `beatPhase` value computed as `Math.sin(time * beatBPM * Math.PI / 30)` in `update()`. This value (range -1 to 1) is sampled by light rays (alpha ±0.05) and orbitals (size ±10%). `beatBPM` scales from 1.0 at follow 1 to 2.0 at follow 5.

**Why a shared sine**: All effects pulsing to the same beat creates coherence. Independent oscillators would look chaotic rather than rhythmic.

**Why subtle amplitude (±5-10%)**: The beat should be felt, not seen. If the pulsation is too obvious, it becomes distracting rather than atmospheric.

### 7. Escalation compression to follow 5

**Decision**: Retune `getStageParams()` thresholds:

| Effect | Current unlock | New unlock | Max at |
|--------|---------------|------------|--------|
| Orbitals | follow 2 | follow 1 | follow 4 |
| Ground glow | follow 2 | follow 1 | follow 4 |
| Nebula | _(new)_ | follow 2 | follow 4 |
| Light rays | follow 4 | follow 2 | follow 5 |
| Comet trail | follow 4 | follow 3 | follow 3 |
| Shockwave | follow 5 | follow 3 | follow 3 |
| Beat sync | _(new)_ | follow 2 | follow 5 |
| Strobe flash | _(new)_ | follow 3 | follow 3 |
| Vortex trails | _(new)_ | follow 1 | follow 3 |
| Orbital comets | _(new)_ | follow 2 | follow 4 |
| Full show | follow 8+ | follow 5 | follow 5 |

**Why not follow 3**: At follow 3 the user hasn't invested enough to justify maximum spectacle. Follow 5 is the "hook point" — enough commitment to reward, few enough that most onboarding users reach it.

### 8. StageParams interface extension

**Decision**: Add new fields to `StageParams`:

```typescript
interface StageParams {
  // ... existing fields ...
  nebulaLayerCount: number       // 0-3
  nebulaAlpha: number            // 0-0.25
  vortexTrailLength: number      // 0-6
  beatBPM: number                // 0-2.0
  strobeEnabled: boolean         // false until follow 3
  orbitalTailArc: number         // 0-45 (degrees)
  orbitalSize: number            // base orbital dot size 2-8
  lightRayWidthMin: number       // 0.08
  lightRayWidthMax: number       // 0.25
}
```

All new fields follow the same pattern: computed from `followCount` in `getStageParams()`, consumed read-only by `OrbRenderer`.

## Risks / Trade-offs

**[Gradient count at max stage] → Mitigation**: At follow 5+, the renderer creates ~20 gradients per frame (3 nebula + 12-16 laser + orb glow). On low-end devices this could cause jank. **Mitigation**: `setParticleScale()` already exists for performance throttling; extend it to also reduce nebula layers and laser count. Add a frame-time check: if `delta > 20ms` for 3 consecutive frames, auto-reduce particle scale.

**[Visual coherence — too many effects] → Mitigation**: All new effects use the same `colorPalette` as source, and `screen` compositing keeps them light-additive. Beat sync ties them to a shared rhythm. If the result is still chaotic, individual effect amplitudes can be tuned down without architectural changes.

**[Test maintenance] → Mitigation**: `stage-effects.spec.ts` boundary values all change. New `StageParams` fields need new assertions. This is straightforward but must be done carefully to avoid false passes on old thresholds.

**[Reduced motion users see degraded experience] → Mitigation**: Vortex trails, beat sync, strobe, and orbital tails are all motion-dependent and will be suppressed. Nebula layers (static overlay) and enlarged orbital dots (static size) still provide visual richness for reduced-motion users.
