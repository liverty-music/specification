## 1. StageParams interface and escalation retuning

- [x] 1.1 Extend `StageParams` interface with new fields: `nebulaLayerCount`, `nebulaAlpha`, `vortexTrailLength`, `beatBPM`, `strobeEnabled`, `orbitalTailArc`, `orbitalSize`, `lightRayWidthMin`, `lightRayWidthMax`
- [x] 1.2 Retune `getStageParams()` thresholds so all effects reach max at follow 5, with earlier unlocks (orbitals at 1, light rays at 2, shockwave/strobe at 3, full show at 5)
- [x] 1.3 Increase orb radius growth per follow (orbRadius 72 at follow 1 instead of 68)

## 2. Vortex flow trails

- [x] 2.1 Add `trail: {x: number, y: number}[]` ring buffer to `OrbParticle` interface
- [x] 2.2 Record particle positions in `update()` and manage ring buffer rotation
- [x] 2.3 Replace single `arc()` draw with tapered `lineTo` trail path in `render()`, respecting reduced motion

## 3. Nebula fill layers

- [x] 3.1 Add `renderNebula()` method to `OrbRenderer` that draws 1-3 rotating radial gradients inside the orb using `screen` compositing
- [x] 3.2 Sample colors from `colorPalette` (fallback to hue 260), rotate each layer at different speeds
- [x] 3.3 Integrate `renderNebula()` into the render pipeline in `dna-orb-canvas.ts`

## 4. Laser show upgrade

- [x] 4.1 Add per-ray `halfWidth` randomization at init (range: `lightRayWidthMin` to `lightRayWidthMax`)
- [x] 4.2 Replace single `fillStyle` with `createLinearGradient` per ray (hue shift +30-60 degrees root-to-tip, fade to transparent)
- [x] 4.3 Add counter-rotating rays (alternate direction flags on init)
- [x] 4.4 Increase max light ray count to 12-16 and max alpha to 0.35-0.4

## 5. Orbital comets

- [x] 5.1 Increase orbital particle size to use `stageParams.orbitalSize` (4-8px) with glow radius `size * 4`
- [x] 5.2 Add trailing arc segment rendering per orbital (`orbitalTailArc` degrees behind current angle, gradient to transparent)

## 6. Strobe flash

- [x] 6.1 Add `strobeFlash` flag to `OrbRenderer`, set on `pulse()` when `strobeEnabled`, cleared after 1 frame
- [x] 6.2 Render full-canvas `fillRect` with `rgba(255,255,255,0.15)` when `strobeFlash` is active
- [x] 6.3 Increase shockwave pool from 3 to 5 slots
- [x] 6.4 Spawn 2-3 staggered shockwaves on `pulse()` when `strobeEnabled` (50ms intervals via accumulated delta)
- [x] 6.5 Add light ray alpha spike to 0.8 on `pulse()`, decaying over 200ms

## 7. Beat sync

- [x] 7.1 Add `beatPhase` calculation in `update()`: `Math.sin(time * beatBPM * PI / 30)`
- [x] 7.2 Apply beat modulation to light ray alpha (±0.1 factor)
- [x] 7.3 Apply beat modulation to orbital size (±10% factor)
- [x] 7.4 Suppress beat sync when `prefers-reduced-motion` is active

## 8. Tests

- [x] 8.1 Update `stage-effects.spec.ts` boundary value tests for new thresholds (follow 0-6, 10, 20) and new fields
- [x] 8.2 Add monotonic growth assertions for new fields (`nebulaLayerCount`, `orbitalTailArc`, `orbitalSize`, `beatBPM`)
- [x] 8.3 Add ceiling assertions for new fields (`nebulaLayerCount <= 3`, `nebulaAlpha <= 0.25`)
- [x] 8.4 Add full-show-at-follow-5 assertion (follow 5 values == follow 6 values for capped params)
- [x] 8.5 Update `orb-renderer.spec.ts` for shockwave pool size (5 concurrent) and any new render state
