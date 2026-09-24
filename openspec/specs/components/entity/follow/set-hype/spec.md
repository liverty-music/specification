# Follow.SetHype

## Purpose

Changes the hype level of an existing Follow.

## Requirements

### Requirement: SetHype changes an existing Follow only

SetHype SHALL set the hype level of the fan's Follow of the artist to the given level, from any level to any other, including to the level it already has. When the fan does not follow the artist, SetHype SHALL fail with NotFound and store nothing.

#### Scenario: Change the level

- **WHEN** the fan follows the artist at Nearby and SetHype is called with Away
- **THEN** the Follow's hype level is Away

#### Scenario: Same level again

- **WHEN** the Follow is at Home and SetHype is called with Home
- **THEN** SetHype succeeds and the level stays Home

#### Scenario: Artist not followed

- **WHEN** the fan does not follow the artist
- **THEN** SetHype fails with NotFound and no Follow is created
