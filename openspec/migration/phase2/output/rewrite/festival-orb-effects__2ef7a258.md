<!-- spec: festival-orb-effects | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Stage-level escalation system -->

### Requirement: Stage-level escalation system
The system SHALL calculate visual effect parameters from the follow count using a stage-level model, where each follow advances the stage by one level. The calculation SHALL be implemented as a pure function, separate from rendering logic. Full visual intensity SHALL be reached at follow 5.

#### Scenario: Stage parameters at zero follows
- **WHEN** the follow count is 0
- **THEN** the stage parameters SHALL be: orb radius 60, orbital count 0, light ray count 0, ground glow intensity 0, shockwave effect off, comet trail effect off, nebula layer count 0, vortex trail length 0, beat tempo (BPM) 0, strobe effect off, orbital tail arc 0, and orbital size 2

#### Scenario: Stage parameters at one follow
- **WHEN** the follow count is 1
- **THEN** the stage parameters SHALL be: orb radius 72, breathing amplitude greater than 0, orbital count 2, particle visibility ratio greater than 0.3, ground glow intensity greater than 0, vortex trail length 2, and orbital size 4

#### Scenario: Stage parameters at two follows
- **WHEN** the follow count is 2
- **THEN** the stage parameters SHALL be: orbital count 5, light ray count 2, nebula layer count 1, beat tempo (BPM) greater than 0, and orbital tail arc greater than 0

#### Scenario: Stage parameters at three follows
- **WHEN** the follow count is 3
- **THEN** the stage parameters SHALL be: shockwave effect on, comet trail effect on, strobe effect on, vortex trail length 6, and light ray count 6

#### Scenario: Stage parameters at four follows
- **WHEN** the follow count is 4
- **THEN** the stage parameters SHALL be: nebula layer count 3, orbital tail arc 45, orbital size 8, and orbital count 11

#### Scenario: Stage parameters at five follows (full show)
- **WHEN** the follow count is 5
- **THEN** the stage parameters SHALL reach maximum intensity: light ray count 12 or more, orbital count 12, beat tempo (BPM) 2.0, light ray intensity 0.35 or more, and all effect features enabled

#### Scenario: Stage parameters at six or more follows
- **WHEN** the follow count is 6 or more
- **THEN** the stage parameters SHALL be the same maximum intensity values as follow 5 (all effects capped at full show level)

#### Scenario: Orb radius growth ceiling
- **WHEN** the follow count exceeds 20
- **THEN** the orb radius SHALL NOT exceed 120

#### Scenario: Stage params are deterministic
- **WHEN** the stage parameters are calculated multiple times with the same follow count
- **THEN** the result SHALL be identical each time (pure function, no side effects)
