<!-- spec: dna-orb-color-injection | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Swirl Animation on Follow -->

### Requirement: Swirl Animation on Follow

The orb SHALL play a swirl animation when a new artist color is injected, making the color mixing visually dynamic.

#### Scenario: Swirl triggers on color injection

- **WHEN** a new artist color is injected into the orb
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
