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
