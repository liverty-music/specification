# DNA Orb Color Injection Specification

## Purpose

Defines how followed-artist bubble hues are injected into discovery orb particles, including the swirl animation triggered on follow.

## Requirements

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
