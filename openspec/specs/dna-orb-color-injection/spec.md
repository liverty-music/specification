## ADDED Requirements

### Requirement: Bubble Hue Injection into Orb Particles

When an artist bubble is absorbed into the DNA orb, the orb's particle system SHALL incorporate the bubble's hue, visually reflecting the followed artist's color identity.

#### Scenario: Follow triggers color injection

- **WHEN** an artist bubble completes its absorption animation into the orb center
- **THEN** the `OrbRenderer` SHALL replace 5-8 existing particles with new particles at the absorbed bubble's hue
- **AND** the replacement SHALL keep the total particle count constant (no net growth)
- **AND** the new particles SHALL have randomized angle, radius, speed, size, and opacity within normal ranges

#### Scenario: Accumulated follows produce diverse orb colors

- **WHEN** a user has followed 3 artists with hues 142 (green), 287 (purple), and 35 (orange)
- **THEN** the orb SHALL contain particles in all three hue families mixed with the base hue range (220-280)
- **AND** the visual effect SHALL be a multi-colored particle swirl representing the user's "Music DNA"

#### Scenario: Hue comes from bubble's existing rendering color

- **WHEN** the absorption animation fires for a bubble
- **THEN** the hue passed to `OrbRenderer.injectColor()` SHALL be the same hue used to render that bubble on the canvas
- **AND** the system SHALL NOT re-compute the hue from the artist name

### Requirement: Swirl Animation on Follow

The orb SHALL play a swirl animation when a new artist color is injected, making the color mixing visually dynamic.

#### Scenario: Swirl triggers on color injection

- **WHEN** `OrbRenderer.injectColor(hue)` is called
- **THEN** the orb's particle rotation speed SHALL increase to 3x normal speed
- **AND** the speed boost SHALL decay smoothly back to 1x over approximately 1000ms
- **AND** the glow intensity SHALL temporarily increase by 0.4 (additive with pulse)

#### Scenario: Swirl during reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the color injection SHALL still occur (particles change hue)
- **BUT** the rotation speed boost SHALL be suppressed (remain at 1x)
- **AND** the glow intensity boost SHALL be suppressed

#### Scenario: Multiple rapid follows

- **WHEN** a user follows two artists in quick succession (within 1 second)
- **THEN** each follow SHALL inject its own color independently
- **AND** the swirl animations SHALL compound (speed boost restarts from 3x on each injection)
- **AND** the particle count SHALL remain constant

## Test Cases

### Unit Tests (Vitest — orb-renderer.spec.ts)

#### TC-ORB-01: injectColor preserves particle count

- **Given** an OrbRenderer initialized with `maxParticles = 60`
- **When** `injectColor(142)` is called
- **Then** `particles.length` SHALL remain 60
- **And** at least 5 particles SHALL have hue within ±10 of 142

#### TC-ORB-02: swirlIntensity set to 1.0 after injectColor

- **Given** an OrbRenderer with `swirlIntensity = 0`
- **When** `injectColor(200)` is called
- **Then** `swirlIntensity` SHALL be `1.0`

#### TC-ORB-03: swirlIntensity decays to 0 after sufficient updates

- **Given** an OrbRenderer after `injectColor(100)` (`swirlIntensity = 1.0`)
- **When** `update(100)` is called 12 times (1200ms total, >1000ms decay window)
- **Then** `swirlIntensity` SHALL be `0`

#### TC-ORB-04: Multiple rapid injectColor calls inject each hue

- **Given** an OrbRenderer
- **When** `injectColor(100)` then `update(200)` then `injectColor(300)` are called
- **Then** `swirlIntensity` SHALL restart to `1.0` on the second call
- **And** particles SHALL contain hues near both 100 and 300

### Unit Tests (Vitest — dna-orb-canvas.spec.ts)

#### TC-ORB-05: Absorption completion threads hue to OrbRenderer

- **Given** a DnaOrbCanvas handling an artist interaction
- **When** `startAbsorption()` is called
- **Then** it SHALL receive the artist's hue and an `onComplete` callback
- **And** when the absorption completes, `orbRenderer.injectColor(hue)` SHALL be called
