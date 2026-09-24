<!-- spec: dna-orb-color-injection | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Bubble Hue Injection into Orb Particles -->

### Requirement: Bubble Hue Injection into Orb Particles

When an artist bubble is absorbed into the DNA orb, the orb's particle system SHALL incorporate the bubble's hue, visually reflecting the followed artist's color identity.

#### Scenario: Follow triggers color injection

- **WHEN** an artist bubble completes its absorption animation into the orb center
- **THEN** the orb's particle system SHALL replace 5-8 existing particles with new particles at the absorbed bubble's hue
- **AND** the replacement SHALL keep the total particle count constant (no net growth)
- **AND** the new particles SHALL have randomized angle, radius, speed, size, and opacity within normal ranges

#### Scenario: Accumulated follows produce diverse orb colors

- **WHEN** a user has followed 3 artists with hues 142 (green), 287 (purple), and 35 (orange)
- **THEN** the orb SHALL contain particles in all three hue families mixed with the base hue range (220-280)
- **AND** the visual effect SHALL be a multi-colored particle swirl representing the user's "Music DNA"

#### Scenario: Hue comes from bubble's existing rendering color

- **WHEN** the absorption animation fires for a bubble
- **THEN** the hue applied to the orb's particle system SHALL be the same hue used to render that bubble on the canvas
- **AND** the system SHALL NOT re-compute the hue from the artist name
