## Why

The recently shipped discovery-page bubble tap feedback does not feel the way it should. The sound effect is synthesized from bare oscillators at a fixed pitch quantized to a pentatonic scale, which produces a mechanical retro-game "beep" rather than the crisp, satisfying pop a bubble should make. The visual effect, meanwhile, animates the bubble being *absorbed* into the central orb (shrink + comet trail) — it never *bursts*. Both miss the tactile delight that makes the core "collect artists by tapping bubbles" loop feel good, so this directly affects the quality of the MVP onboarding experience.

## What Changes

- Replace the tap sound effect with a single fixed, crisp "pu-chu" pop, synthesized procedurally via Web Audio. During iteration the per-bubble pentatonic pitch mapping and rapid-tap combo were intentionally dropped — every tap now plays the same pop, which feels cleaner than the musical mapping for this interaction:
  - A low, lippy plosive "pu" thump (with a filtered-noise breath) fires first.
  - A short, dry high "chu" chirp — a fast downward pitch drop through a lightly resonant low-pass — fires a short beat later, so the pop reads as two distinct parts.
  - Short percussive decays keep it crisp; low resonance keeps it dry, not wet/wobbly.
  - Replace the post-absorption "settle" with a soft, low fixed landing tone.
- Change the bubble tap visual from "absorb only" to "burst, then absorb": the bubble visibly pops in place (brief over-inflation → bright rupture ring + additive light bloom → outward spray of luminous color droplets) before the existing color-injection absorption continues toward the orb. The orb color-injection metaphor is preserved.
- Continue to respect `prefers-reduced-motion` (burst suppressed) and the existing mute/volume settings.

## Capabilities

### New Capabilities
- `discovery-tap-sonic-feedback`: Defines the procedural sound-effect behavior for tapping artist bubbles on the discovery page — a single fixed two-part "pu-chu" pop (low plosive thump + delayed high downward chirp, noise breath, dry percussive timbre, identical on every tap with no scale/combo), the post-absorption landing tone, and respect for mute/volume preferences.

### Modified Capabilities
- `artist-discovery-dna-orb-ui`: The "Bubble Absorption Animation" requirement changes so that tapping a bubble first plays a burst (over-inflation → bright rupture ring + additive light bloom → luminous color-droplet spray at the tap point) and then proceeds into the existing absorption-into-orb animation, rather than going straight to absorption.

## Impact

- Frontend only (`frontend/`); no proto, backend, or BSR changes.
- Affected code:
  - `src/services/audio-engine.ts` — `spawnVoice` (pitch envelope + low-pass + noise transient), `playTap`, `playLanding`.
  - `src/components/dna-orb/tap-effects.ts` — the press/squash feedback becomes over-inflation + rupture ring.
  - `src/components/dna-orb/absorption-animator.ts` — dissolve-particle spawn reused/retuned as the burst spray (tap point, bubble hue, immediate, denser).
  - `src/components/dna-orb/dna-orb-canvas.ts` — orchestration order of tap → burst → absorb.
- No new audio assets; synthesis stays fully procedural.
- Scope excludes recorded audio samples, any non-discovery screens, and backend/proto work.
