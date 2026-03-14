## 1. Stage Effects Module

- [x] 1.1 Create `src/components/dna-orb/stage-effects.ts` with `StageParams` interface and `getStageParams(followCount)` pure function
- [x] 1.2 Implement parameter curves: orbRadius (60→120, linear then log), breathAmplitude, breathSpeed, orbitalCount (0→12), lightRayCount (0→6), lightRayAlpha, groundGlowAlpha, shockwaveEnabled, cometTrailEnabled, particleVisibilityRatio
- [x] 1.3 Create `src/components/dna-orb/stage-effects.spec.ts` — boundary value tests at follow counts 0, 1, 2, 3, 4, 5, 6, 10, 20; monotonic growth assertions; ceiling assertions (orbRadius ≤ 120, orbitalCount ≤ 12)

## 2. Growing Orb & Dynamic Physics Boundary

- [x] 2.1 In `bubble-physics.ts`, add `updateOrbZone(orbRadius: number)` method that repositions the bottom wall to `canvasHeight - (orbRadius * 2 + 20)` using `Matter.Body.setPosition()`
- [x] 2.2 In `orb-renderer.ts`, change `orbRadius` from fixed 70 to a dynamic value set by `setFollowCount()` using `stageParams.orbRadius`
- [x] 2.3 In `orb-renderer.ts`, add breathing pulse: multiply orbRadius by `1 + sin(time * breathSpeed) * breathAmplitude`, suppress when `prefers-reduced-motion`
- [x] 2.4 In `dna-orb-canvas.ts`, wire `followedCountChanged` to call `physics.updateOrbZone(stageParams.orbRadius)` and pass new radius to `orbRenderer`

## 3. Orbital Particles

- [x] 3.1 In `orb-renderer.ts`, add pre-allocated orbital slots (max 12) with angle, orbitalRadius (1.3-1.8x orbRadius), speed, size (2-5px), hue
- [x] 3.2 In `update()`, rotate orbitals by their angular velocity (suppress rotation for reduced motion)
- [x] 3.3 In `render()`, draw visible orbitals (count from stageParams) as small radial gradient glow dots after the orb body, sampling colors from the color palette

## 4. Light Rays

- [x] 4.1 In `orb-renderer.ts`, add light ray rendering: triangular gradients from orb center, count and alpha from stageParams
- [x] 4.2 Add slow rotation over time (fixed angle for reduced motion)
- [x] 4.3 Use `globalCompositeOperation = 'screen'` wrapped in `save()/restore()`, render before bubbles (layer 1)

## 5. Shockwave Rings

- [x] 5.1 In `orb-renderer.ts`, add shockwave ring pool (max 3): `spawnShockwave(hue)` method that initializes radius at orbRadius, alpha at 0.6, lineWidth at 3
- [x] 5.2 In `update()`, expand radius to orbRadius×3 over 800ms, decay alpha to 0, decrease lineWidth to 0.5; mark inactive on completion
- [x] 5.3 In `render()`, draw active shockwave rings as `arc()` + `stroke()` after orbitals
- [x] 5.4 Suppress shockwave spawning when `prefers-reduced-motion`

## 6. Comet Trail on Absorption

- [x] 6.1 In `absorption-animator.ts`, add `trailPoints` circular buffer (max 12) to `AbsorptionAnimation`; record current position each frame when `cometTrailEnabled` is true
- [x] 6.2 In `render()`, draw trail as segmented lines: width 4→1px, opacity 0.7→0.05, colored with artist hue; render before the absorption bubble body (layer 3)
- [x] 6.3 Pass `cometTrailEnabled` from `dna-orb-canvas.ts` to the absorption animator based on current stageParams

## 7. Ground Glow

- [x] 7.1 In `orb-renderer.ts`, add ground glow rendering: vertical linearGradient at bottom 15% of canvas, alpha from stageParams, hue from dominant palette color
- [x] 7.2 Use `globalCompositeOperation = 'screen'` wrapped in `save()/restore()`, render as layer 0 (behind everything)

## 8. Color Palette Accumulation

- [x] 8.1 In `orb-renderer.ts`, add `colorPalette: number[]` (max 20, FIFO on overflow) populated by `injectColor()`
- [x] 8.2 Distribute palette colors to orbital particles and light rays (evenly across entries)

## 9. Render Pipeline & Orchestration

- [x] 9.1 In `dna-orb-canvas.ts`, update `render()` to draw layers in order: ground glow → light rays → bubbles → comet trails → absorption → orb body → orbitals → shockwaves
- [x] 9.2 Wire absorption completion to trigger `orbRenderer.spawnShockwave(hue)` in addition to existing `injectColor(hue)`
- [x] 9.3 Replace `orbIntensity` scalar usage with stageParams-driven rendering throughout

## 10. Remove Orb Label

- [x] 10.1 Delete the `orb-label` div from `discover-page.html`
- [x] 10.2 Delete `.orb-label` CSS rules from `discover-page.css`
- [x] 10.3 Verify screen reader status text (`srStatusText`) still reports follow count

## 11. OrbRenderer & AbsorptionAnimator Unit Tests

- [x] 11.1 Create `src/components/dna-orb/orb-renderer.spec.ts` — shockwave lifecycle (spawn → 800ms update → inactive), color palette FIFO cap at 20, orbital count reflects stageParams
- [x] 11.2 Create `src/components/dna-orb/absorption-animator.spec.ts` — trail buffer accumulates to max 12, trail disabled when cometTrailEnabled is false
- [x] 11.3 Test `prefers-reduced-motion` suppression: breathing amplitude 0, orbital rotation suppressed, shockwave suppressed

## 12. Integration & Polish

- [x] 12.1 Run `make check` (lint + test) and fix any failures
- [x] 12.2 Manual visual testing: verify each stage level (0-6+) produces visibly distinct escalation
- [x] 12.3 Performance verification: confirm 60fps on mobile emulation with all effects active at stage 6+
