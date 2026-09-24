<!-- spec: onboarding-guidance | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Orb pulse on follow -->

### Requirement: Orb pulse on follow
The central Music DNA orb SHALL pulse each time an artist is followed, providing visual feedback that the selection was registered.

#### Scenario: Bubble tap triggers orb pulse
- **WHEN** a bubble is tapped and the follow operation succeeds
- **THEN** the `DnaOrbCanvas.followedCountChanged` callback SHALL fire
- **AND** the orb SHALL play a pulse animation
- **AND** the orb's `baseIntensity` SHALL increase according to the easing curve
