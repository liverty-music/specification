## Why

The DNA Orb's visual effects plateau quickly — by 6 follows, `effectiveIntensity` is already capped at 1.0, yet the orb looks static and subdued. The fixed 70px radius, limited blue-purple palette, and 1-second swirl decay fail to convey the excitement of building a music identity. The onboarding experience should feel like arriving at a festival where the lights escalate with every act, not watching a screensaver.

## What Changes

- **Growing orb**: Orb radius scales from 60px → 120px based on follow count, pushing the bubble area upward via dynamic Matter.js wall repositioning
- **Stage-level escalation system**: Each follow advances a "stage level" that unlocks new visual effects (breathing pulse → orbital particles → light rays → shockwave rings), replacing the current single `orbIntensity` scalar
- **Orbital particles**: Glowing particles orbit outside the orb, increasing in count and speed per stage level
- **Light rays**: Radial beams emanate from the orb (stage 4+), rotating slowly with `screen` composite blending for additive light
- **Shockwave rings**: Expanding color rings burst from the orb on each follow
- **Comet trail on absorption**: Absorbed bubbles leave a colored polyline trail (8-12 frame positions) that fades along the path
- **Ground glow**: Soft gradient reflection at the screen bottom, intensity tied to stage level
- **Color palette accumulation**: Artist hues are stored in a palette array, enriching orbital and ray colors toward a rainbow spectrum
- **Remove "MUSIC DNA · N" label**: The orb-label element and associated CSS are deleted
- **Unit test coverage**: `stage-effects.ts` (pure parameter calculation) and visual effect state transitions are covered by Vitest tests

## Capabilities

### New Capabilities

- `festival-orb-effects`: Stage-level escalation system, orbital particles, light rays, shockwave rings, comet trails, ground glow, and growing orb behavior

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: Orb visual evolution requirements change from intensity-scalar model to stage-level model; orb-label requirement is removed; absorption animation gains comet trail; orbZoneHeight becomes dynamic

## Impact

- **Frontend components**: `orb-renderer.ts` (major rewrite), `absorption-animator.ts` (comet trail), `bubble-physics.ts` (dynamic wall), `dna-orb-canvas.ts` (orchestration + render order)
- **New file**: `stage-effects.ts` — pure calculation of stage parameters from follow count
- **Template/CSS**: `discover-page.html` (remove orb-label), `discover-page.css` (remove `.orb-label` rules)
- **Tests**: New test files for `stage-effects.ts` and effect state transitions
- **No backend changes**: Purely frontend visual enhancement
- **Performance**: Additional Canvas draw calls (orbitals, rays, glow); mitigated by existing FPS monitoring and quality scaling
