## Why

The DNA Orb's current visual effects are too subtle to create excitement during the follow action. Inner particles are small dots (1-3px), light rays are few and monochrome, orbital particles lack presence, and the orb interior feels empty as it grows. The escalation takes 8+ follows to reach full effect, which is too slow to reward users during onboarding. We need concert-grade visual intensity that reaches its peak at follow 5 to make every follow feel impactful and the experience feel like a live music event.

## What Changes

- **Vortex Flow**: Replace scattered inner dot particles with fluid-like swirling trails that create a water vortex effect inside the orb. Each particle draws a tapered trail of its recent positions.
- **Nebula Fill**: Add 2-3 layered radial gradients that slowly rotate inside the orb, filling empty space with colorful nebula clouds that use the accumulated color palette.
- **Laser Show upgrade**: Increase max light rays from 6 to 12-16, add per-ray linear gradients (root-to-tip color shift), randomize beam widths, mix in counter-rotating rays, and add tip flares.
- **Orbital Comets**: Enlarge orbital particles (4-8px), add comet tails trailing each orbital, increase glow radius, and introduce elliptical orbit paths at higher stages.
- **Strobe Flash**: Add a brief full-canvas white flash on follow, stagger 2-3 rapid shockwaves, and spike all light ray alpha momentarily.
- **Beat Sync**: Add a subtle BPM-style pulsation (synced sine wave) that modulates light ray alpha, orbital glow, and orb radius to create rhythmic "breathing" that increases tempo with follow count.
- **Escalation retuning**: Compress the full-show unlock from follow 8 to follow 5. All effects visible and at maximum intensity by the 5th follow.

## Capabilities

### New Capabilities

_(none — all effects are enhancements to the existing festival-orb-effects capability)_

### Modified Capabilities

- `festival-orb-effects`: Stage escalation compressed to follow 5 max. Six new visual layers added (vortex trails, nebula fill, laser gradients, orbital comets, strobe flash, beat sync). All existing `StageParams` thresholds and max values change.

## Impact

- **Frontend only** — all changes are in `src/components/dna-orb/` (orb-renderer.ts, stage-effects.ts, dna-orb-canvas.ts)
- **No backend or API changes**
- **No new dependencies** — all effects use Canvas 2D APIs already in use
- **Test updates** — `stage-effects.spec.ts` and `orb-renderer.spec.ts` boundary values change due to retuned thresholds
- **Performance budget** — additional gradient and lineTo calls; estimated well within 60fps on mobile at max orb radius (120px fill area)
