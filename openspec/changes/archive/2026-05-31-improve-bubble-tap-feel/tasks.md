## 1. Audio: fixed "pu-chu" pop (`src/services/audio-engine.ts`)

- [x] 1.1 Add a cached white-noise `AudioBuffer` generated once on the engine (reused for every tap breath)
- [x] 1.2 Extend `ToneOptions` to support an optional pitch drop (start ratio + duration), an optional low-pass cutoff sweep (start/end cutoff, Q), and a per-voice start `delay`
- [x] 1.3 Rework `spawnVoice` graph to `osc → (optional lowpass) → gain → master`; schedule a downward `frequency.exponentialRampToValueAtTime`; honor the start `delay`
- [x] 1.4 Add an optional short filtered-noise breath layer (`AudioBufferSourceNode → lowpass → fast-decay gain → master`) fired at the voice's start time, self-disconnecting on end
- [x] 1.5 Build `playTap` as a single fixed two-part "pu-chu" pop — a low lippy plosive thump (with noise breath) then a delayed (~22ms) high downward `triangle` chirp through a lightly-resonant low-pass — ignoring `hue` so every tap is identical
- [x] 1.6 Remove the pentatonic mapping, rapid-tap combo, and overtone (pivoted to one fixed pop): delete `PENTATONIC`/MIDI-scale helpers, `advanceCombo`/combo state, and the exported `hueToPentatonicPitch`
- [x] 1.7 Update `playLanding` to a soft, low fixed settle tone (downward `sine` "boop"; no hue derivation, no noise breath)
- [x] 1.8 Confirm mute/volume gating and lazy `unlock` behavior are unchanged

## 2. Visual: burst then absorb (`src/components/dna-orb/`)

- [x] 2.1 In `tap-effects.ts`, replace the horizontal-squash press with an over-inflation anticipation (scale ~1.0 → ~1.15 over ~40ms) that still fires the `onRelease`/peak callback to start absorption
- [x] 2.2 In `tap-effects.ts`, add a bright rupture ring plus an additive light bloom (`globalCompositeOperation = 'lighter'`) that flash open at the burst point
- [x] 2.3 In `absorption-animator.ts`, add `spawnBurst` (reusing the particle pool): emit at the tap point, immediately, tinted with the bubble's hue, denser (15–20), slightly larger, with downward gravity, and render luminously (additive glow halo + white-hot core)
- [x] 2.4 In `dna-orb-canvas.ts` `handleInteraction`, re-order to: tap feedback (audio+haptic) → burst (over-inflation + rupture ring/light bloom + luminous droplet spray) → on burst peak start existing absorption (comet trail + `injectColor` + shockwave)
- [x] 2.5 Ensure `prefers-reduced-motion` suppresses over-inflation, rupture ring/bloom, and droplet spray and falls straight through to absorption

## 3. Tests & verification

- [x] 3.1 `audio-engine` unit tests cover the pure `glideStartFreq` drop math (start above target, positive, proportional); the pentatonic tests were removed with the mapping. (The imperative Web Audio graph is verified by typecheck and in-app, since jsdom has no AudioContext and the engine resolves DI in its constructor.)
- [x] 3.2 Update/extend `dna-orb` / tap-effect unit tests: assert burst-before-absorb staging, luminous droplet spray uses the bubble hue at the tap point with a white-hot core, and reduced-motion suppresses the burst
- [x] 3.3 Run `make check` (Biome lint + format + typecheck + vitest) and fix any failures
- [x] 3.4 Verify by ear and eye in the running app (local backend + `npm start`): every tap plays the same crisp "pu-chu" pop, and the bubble visibly bursts (luminous spray + light bloom) before its color flies into the orb. Audio constants tuned by ear to the approved character.
- [x] 3.5 Verify reduced-motion and muted paths behave correctly in the running app
