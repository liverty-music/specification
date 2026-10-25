# Set Hype

## Purpose

FollowUseCase.SetHype changes the hype level of an artist the fan already follows, which changes which of the artist's future concerts reach the fan by push.

## Requirements

### Requirement: SetHype stores any hype level on the fan's Follow

SetHype SHALL set the fan's Follow of the artist to the given hype level through Follow.SetHype and accept every hype level: Watch, Home, Nearby and Away. When the fan does not follow the artist, SetHype SHALL fail with NotFound.

#### Scenario: Fan raises the hype level

- **WHEN** a fan who follows an artist at Nearby sets it to Away
- **THEN** the Follow is at Away and SetHype succeeds

#### Scenario: Every level accepted

- **WHEN** a fan sets the hype level to Watch, Home, Nearby or Away
- **THEN** SetHype stores that level

#### Scenario: Artist not followed

- **WHEN** a fan sets the hype level of an artist they do not follow
- **THEN** SetHype fails with NotFound

### Requirement: SetHype reports each hype level set

After the hype level is set, SetHype SHALL send a "hype set" signal for product analytics carrying the fan, the artist, the level set and the time it was set. The previous level is not part of the signal: it is the level of the fan's previous signal for the artist, or the default level at follow. A failure to send the signal SHALL NOT fail SetHype and SHALL NOT undo the change.

#### Scenario: Hype raised
- **WHEN** a fan changes an artist from watch to away
- **THEN** a signal is sent with the level away and the time it was set

#### Scenario: Signal failure
- **WHEN** the signal cannot be sent
- **THEN** SetHype succeeds and the level stays away
