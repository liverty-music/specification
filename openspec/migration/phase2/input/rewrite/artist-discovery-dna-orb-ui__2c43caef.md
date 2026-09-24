<!-- spec: artist-discovery-dna-orb-ui | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Combined spawn-and-absorb bubble action -->

### Requirement: Spawn and absorb API on canvas
The `DnaOrbCanvas` component SHALL expose a `spawnAndAbsorb` method that combines spawning a temporary bubble and immediately starting its absorption animation.

#### Scenario: spawnAndAbsorb creates and absorbs a bubble
- **WHEN** `spawnAndAbsorb(artist, x, y)` is called
- **THEN** the canvas SHALL start the absorption animation from (x, y) toward the orb center
- **AND** on completion, the canvas SHALL call `orbRenderer.injectColor()` with the artist's hue
- **AND** the canvas SHALL **immediately** dispatch the `need-more-bubbles` custom event (not deferred until absorption completion)

---
