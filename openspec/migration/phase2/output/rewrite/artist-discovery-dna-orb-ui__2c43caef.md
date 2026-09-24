<!-- spec: artist-discovery-dna-orb-ui | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Combined spawn-and-absorb bubble action -->

### Requirement: Combined spawn-and-absorb bubble action
The system SHALL expose a combined action that spawns a temporary bubble and immediately starts its absorption animation into the orb.

#### Scenario: Spawn-and-absorb creates and absorbs a bubble
- **WHEN** the spawn-and-absorb action is invoked for an artist at a given position
- **THEN** the canvas SHALL start the absorption animation from that position toward the orb center
- **AND** on completion, the canvas SHALL inject the artist's color into the orb
- **AND** the canvas SHALL **immediately** dispatch the `need-more-bubbles` custom event (not deferred until absorption completion)
