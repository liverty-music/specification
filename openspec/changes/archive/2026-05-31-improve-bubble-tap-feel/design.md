## Context

The discovery page renders artist bubbles on an HTML5 Canvas with Matter.js physics. Tapping a bubble triggers three things today:

1. **Audio** — `AudioEngine.playTap(hue)` synthesizes a tone with bare `OscillatorNode`s (`triangle` + optional `sine` overtone), at a **fixed** frequency (`osc.frequency.setValueAtTime(freq, t)`), where `freq` is the bubble hue quantized to a major pentatonic scale. A rapid-tap combo climbs the scale. `playLanding(hue)` plays a softer tone an octave down when absorption completes.
2. **Press feedback** — `TapEffects.addPress` squashes the bubble horizontally for ~70ms, then fires a callback.
3. **Absorption** — `AbsorptionAnimator` shrinks the bubble and flies it into the orb along a Bézier path with a comet trail, spawning ~15 generic dissolve particles (hue 220–280) near the orb at 85% progress.

Two problems:

- **Sound**: a constant-pitch pure oscillator quantized to a scale is, by construction, a chiptune beep. The timbre — not the note choice — is what reads as "mechanical / retro game".
- **Visual**: the dominant motion is "absorbed into the orb", never "burst". There is no pop.

Constraints carried forward:
- Frontend-only change; no proto/backend/BSR work.
- No recorded audio assets — synthesis stays fully procedural so pitch can keep deriving from hue.
- Must respect `prefers-reduced-motion` and the existing mute/volume settings.
- Web Audio is the only sound API; the AudioContext is created lazily inside a user gesture (`unlock`).

## Goals / Non-Goals

**Goals:**
- Make the tap SE read as a crisp, satisfying two-part "pu-chu" pop rather than a retro beep. (During in-app tuning the per-bubble pentatonic pitch and rapid-tap combo were intentionally dropped in favor of a single identical pop — see D3.)
- Make the bubble visibly **burst** on tap (strong: dense luminous color-droplet spray + bright rupture ring + light bloom), then continue into the existing absorption-into-orb so the color-injection metaphor survives.
- Keep latency low (tap feedback must remain perceptually immediate) and CPU bounded (voice cap, particle pool reuse).

**Non-Goals:**
- Introducing recorded audio samples or an audio asset pipeline.
- Changing the orb color-injection behavior, stage-effect escalation, or absorption trajectory itself.
- Touching any screen other than discovery, or any backend/proto surface.
- Adding a new audio settings surface (mute/volume behavior is unchanged).

## Decisions

### D1: Procedural synthesis, not a recorded sample

Keep `AudioEngine` fully procedural. The fixed "pu-chu" pop is built from several very short, tightly-scheduled layers (a low thump, a delayed downward chirp, a noise breath) with millisecond-level envelopes — synthesis gives precise control over those transients with zero asset weight, which suits a PWA.

*Alternative considered:* one high-quality recorded "pop" sample. Rejected — adds an asset to manage and ship for a PWA, and the crisp two-part pop is fully achievable in synthesis (see D2). (Procedural also kept the door open during the by-ear tuning that converged on the final character.)

### D2: Fixed "pu-chu" pop = plosive thump + delayed downward chirp + noise breath

> **Iteration note.** The voice was tuned by ear in the running app. An ascending
> glide read as a mechanical "blip"; a fast downward drop read as a dull "pon";
> a resonant up-curl read as a wet "puryu" but then as a thin "chu". The version
> that landed is a **two-part fixed pop**, below. Each tap plays this identical
> pop — see D3 for why the musical mapping was dropped.

Build the pop from two short layered voices per tap:

- **"pu" thump (low, first).** A `sine` near ~160Hz with a quick downward drop and a short decay (~30ms), carrying the plosive noise breath. This is the lippy front of the pop.
- **"chu" chirp (high, a beat later).** A `triangle` near ~820Hz whose pitch drops fast from above (start ≈ 2.4× the target) onto the target via `frequency.exponentialRampToValueAtTime`, through a **lightly** resonant low-pass (`Q ≈ 1.5`, so dry/crisp — not wet). Scheduled ~22ms after the "pu" (via a per-voice `delay`) so the ear hears two distinct parts.
- **Noise breath.** A very short (~9ms) low-pass-filtered (~2kHz, lippy not bright) white-noise burst at the "pu" attack. Buffer generated once and cached.
- **Amplitude envelopes.** Near-instant attack, short percussive decays (~30ms "pu", ~45ms "chu"), `exponentialRampToValueAtTime` to near-zero — crisp, no sustained tail.

`spawnVoice` is "osc → (optional lowpass) → gain → master" with optional pitch-drop, cutoff sweep, `Q`, `delay`, and a noise layer. The voice cap (`MAX_VOICES`) and `onended` cleanup are retained; the noise source self-disconnects.

*Alternatives considered (all auditioned in-app):* ascending glide (mechanical blip), pure downward drop (dull "pon"), resonant wet up-curl (wet "puryu" / thin "chu"). The two-part "pu-chu" was the one that read as a crisp, satisfying pop.

### D3: No musical scale, no combo — every tap is the same pop

The original hue→pentatonic pitch mapping and the rapid-tap combo are **removed**. During tuning it became clear that a single identical pop feels cleaner and punchier for this tap interaction than a melodic mapping, and the user explicitly chose "all taps the same SE". Consequently `PENTATONIC`, the MIDI/scale helpers, `advanceCombo`, the combo/overtone state, and the exported `hueToPentatonicPitch` are deleted. `playTap(hue)` ignores its `hue` argument (kept only to preserve the `IAudioEngine` signature and the call site).

### D4: `playLanding` is a fixed low settle

The post-absorption "settle" tone is a soft, low fixed `sine` "boop" that settles downward in pitch. It no longer derives from the bubble's hue and omits the noise breath — consistent with the fixed-pop direction.

### D5: Visual — "burst, then absorb" (Plan B), strong burst

Re-stage the tap so the bubble pops in place before the existing absorption runs. New ordering in `dna-orb-canvas.ts` `handleInteraction`:

```
tap
 ├─ emitTapFeedback(hue)        // audio (pu-chu pop) + haptic — immediate, unchanged call site
 ├─ TapEffects: BURST
 │    1. over-inflation   scale 1.0 → ~1.15 over ~40ms   (membrane tension before rupture)
 │    2. rupture ring     bright ring + additive light bloom at the burst point
 │    3. droplet spray    15–20 LUMINOUS droplets at the TAP POINT, tinted with the
 │                        BUBBLE'S hue, emitted immediately, outward + gravity arc, fade
 ├─ physics.removeBubble
 └─ onBurstPeak → AbsorptionAnimator.startAbsorption(...)   // existing comet→orb→injectColor
```

- The current `addPress` **horizontal squash** is replaced by the **over-inflation** anticipation (a bubble at its tension limit swells, then ruptures). The existing `onRelease` callback contract (fire after the anticipation pre-roll to start absorption) is preserved — only the visual and timing change.
- The **rupture ring** is a brighter, faster variant of the existing ripple drawn at the burst radius, plus an **additive light bloom** (white→hue radial gradient, `globalCompositeOperation = 'lighter'`) so the burst reads as a pop of light against the dark canvas.
- The **droplet spray** reuses `AbsorptionAnimator.spawnDissolveParticles`, retuned into a `spawnBurst`: spawn at the **tap point** (not at 85% near the orb), **immediately** (not at 85% progress), tinted with the **bubble's hue** (not fixed 220–280), denser (15–20), slightly larger, with a small downward gravity term so droplets arc like flung water. Burst droplets render **luminously** (additive glow halo + white-hot core) so they read as sparks of light, not flat same-color dots.
- After the burst peak, the **existing** absorption (shrink + comet trail + `injectColor` + shockwave) runs unchanged, so "the artist's color flies into your orb" is intact.

*Alternative considered:* Plan A (pure burst, no absorption) — rejected because it discards the orb color-injection metaphor that `dna-orb-color-injection` and stage escalation depend on. Plan C (burst + thin single color streak) — viable but a bigger rewrite of the absorption visual; deferred.

### D6: Accessibility & settings unchanged in contract

`prefers-reduced-motion` suppresses the burst (over-inflation, ring, spray) exactly as it suppresses ripple/press today, falling straight through to absorption (which already has its own reduced-motion handling). Mute/volume continue to gate all audio via the master gain. No new settings surface.

## Risks / Trade-offs

- **Synthesized pop may not feel organic enough** → Mitigated by tuning the constants by ear in the running app until the "pu-chu" landed; the constants are named and grouped at the top of `audio-engine.ts` so further tuning is cheap. If synthesis ever can't land the feel, D1 (a recorded sample) can be revisited.
- **Multiple short voices + noise source per tap raise per-tap cost** → Bounded by the existing `MAX_VOICES` cap; the noise buffer is generated once and reused. Rapid tapping is the worst case and stays within the voice cap.
- **Denser, immediate droplet spray adds canvas draw load on low-end mobile** → Reuse the existing particle pool (no new allocations per tap), cap droplet count (≤20), and short lifetimes. Burst is fully suppressed under reduced-motion.
- **Audio timing glitches if envelopes overlap** → Use `exponentialRampToValueAtTime` with a small floor (avoid 0 for exponential ramps, as the code does with `0.0001`) and schedule all ramps relative to the voice's start time at spawn.
- **Tests asserting the old pentatonic / squash behavior break** → Resolved: pentatonic unit tests were removed with the mapping; `audio-engine` tests now cover the pure `glideStartFreq` drop math, and `dna-orb`/tap-effect tests cover burst-before-absorb staging, luminous-droplet hue at the tap point, and reduced-motion suppression.

## Open Questions

- The exact tuned millisecond/Hz constants (`PLOSIVE_FREQ`, `CHU_DELAY`, `POP_FREQ`, decays, cutoffs, `NOISE_*`) were dialed in by ear and are grouped at the top of `audio-engine.ts` for easy future adjustment; the spec fixes the *behavior* (fixed two-part "pu-chu" pop, no scale/combo), not the constants.
- Whether haptics should also change cadence to match the burst — left as-is (out of scope).
