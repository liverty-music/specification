## ADDED Requirements

### Requirement: SetHype reports each hype level set

After the hype level is set, SetHype SHALL send a "hype set" signal for product analytics carrying the fan, the artist, the level set and the time it was set. The previous level is not part of the signal: it is the level of the fan's previous signal for the artist, or the default level at follow. A failure to send the signal SHALL NOT fail SetHype and SHALL NOT undo the change.

#### Scenario: Hype raised
- **WHEN** a fan changes an artist from watch to away
- **THEN** a signal is sent with the level away and the time it was set

#### Scenario: Signal failure
- **WHEN** the signal cannot be sent
- **THEN** SetHype succeeds and the level stays away
