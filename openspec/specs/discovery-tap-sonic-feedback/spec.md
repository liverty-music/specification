# Discovery Tap Sonic Feedback

## Purpose

This capability defines the procedural sound effect played when a user taps an artist bubble on the discovery page. It specifies a single fixed, crisp two-part "pu-chu" pop (synthesized via the Web Audio API, no recorded assets), the soft settle tone on absorption completion, and respect for the user's mute/volume preferences and the browser autoplay policy.

---

## Requirements

### Requirement: Bubble Tap Sound Character

The discovery page SHALL play a single fixed two-part "pu-chu" pop sound effect when a user taps an artist bubble, synthesized procedurally via the Web Audio API (no recorded audio assets), such that the tap reads as a crisp, satisfying bubble pop rather than a retro-game tone. Every tap SHALL sound identical — there is no musical scale, no per-bubble pitch, and no combo.

#### Scenario: Tap plays a fixed pop on every tap
- **WHEN** a user taps an artist bubble and audio is unlocked and not muted
- **THEN** the system SHALL play the same fixed pop regardless of which bubble is tapped
- **AND** the pop SHALL NOT vary in pitch with the bubble's hue or with how rapidly taps occur

#### Scenario: Pop is a low "pu" thump followed by a high "chu" chirp
- **WHEN** the tap pop is synthesized
- **THEN** a low-pitched plosive "pu" thump SHALL fire first
- **AND** a higher-pitched "chu" chirp SHALL fire a short beat later (on the order of ~20ms) so the pop reads as two distinct parts
- **AND** the "chu" chirp's pitch SHALL drop quickly from above onto its target pitch (a fast downward chirp animated with a Web Audio frequency ramp, not held constant)

#### Scenario: Pop has a plosive noise breath
- **WHEN** the "pu" thump begins
- **THEN** a short low-pass-filtered noise burst SHALL be layered at its attack to provide the lippy plosive onset

#### Scenario: Pop timbre is dry and percussive
- **WHEN** the pop plays
- **THEN** each voice's amplitude SHALL rise quickly and decay to near-silence within a short interval (a short percussive tail, not a sustained tone)
- **AND** the low-pass resonance SHALL be low so the pop reads as dry and crisp rather than wet or wobbly

---

### Requirement: Landing Tone On Absorption

When a tapped bubble completes its absorption into the orb, the system SHALL play a soft, low fixed settle ("landing") tone.

#### Scenario: Absorption completion plays a settle tone
- **WHEN** a bubble finishes being absorbed into the orb
- **THEN** the system SHALL play a soft, low fixed tone that settles downward in pitch
- **AND** the tone SHALL be the same on every absorption (it does not derive from the bubble's hue) and SHALL omit the plosive noise breath

---

### Requirement: Sound Respects Mute and Volume Settings

The tap and landing sounds SHALL honor the user's existing mute and volume preferences and the browser autoplay policy.

#### Scenario: Muted user taps a bubble
- **WHEN** the user has muted sound and taps a bubble
- **THEN** no audible tap or landing tone SHALL be produced

#### Scenario: Volume preference applied
- **WHEN** the user has set a volume level
- **THEN** the tap and landing tones SHALL be scaled to that level via the master output

#### Scenario: Audio unlocked within a user gesture
- **WHEN** audio has not yet been unlocked by a user gesture
- **THEN** no AudioContext SHALL be forcibly started outside a gesture, consistent with the existing lazy-unlock behavior
