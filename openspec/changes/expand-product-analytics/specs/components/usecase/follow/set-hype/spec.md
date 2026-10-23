## ADDED Requirements

### Requirement: SetHype reports each actual hype change

After the hype level is set, SetHype SHALL send a "hype changed" signal for product analytics carrying the fan, the artist, the previous level and the new level. It SHALL send no signal when the new level equals the previous one. A failure to send the signal SHALL NOT fail SetHype and SHALL NOT undo the change.

#### Scenario: Hype raised
- **WHEN** a fan changes an artist from watch to away
- **THEN** a signal is sent with previous level watch and new level away

#### Scenario: Same level
- **WHEN** a fan sets the level the follow already has
- **THEN** no signal is sent
