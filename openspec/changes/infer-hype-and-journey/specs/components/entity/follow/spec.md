## MODIFIED Requirements

### Requirement: A new Follow starts at Nearby

A new Follow SHALL start with hype level Nearby, set by default.

#### Scenario: Fan follows an artist

- **WHEN** a Follow is created for a fan and an artist
- **THEN** its hype level is Nearby and its hype set by is default

## ADDED Requirements

### Requirement: The lowest hype level that matches a concert

Given a concert and the fan's home, the lowest hype level that matches the concert SHALL be the lowest of Watch, Home, Nearby and Away whose matched concerts include it: Home for a concert in the home area, Nearby for one whose proximity is Nearby, and Away for one known to be farther than the nearby range. When the concert is outside the home area and its distance from the home cannot be measured, because the venue's location or the home's center is unknown, there SHALL be no lowest matching level: nothing shows how far the fan travels for it.

#### Scenario: Concert in the home area

- **WHEN** the fan's home area is JP-13 and the concert is in JP-13
- **THEN** the lowest matching hype level is Home

#### Scenario: Nearby concert

- **WHEN** the concert's proximity to the fan's home is Nearby
- **THEN** the lowest matching hype level is Nearby

#### Scenario: Distant concert

- **WHEN** the concert's venue is more than 200 km from the center of the fan's home area
- **THEN** the lowest matching hype level is Away

#### Scenario: Venue location unknown

- **WHEN** the fan's home area is JP-13 and the concert's venue has neither a known area nor a known location
- **THEN** there is no lowest matching hype level

### Requirement: The app may raise only a hype level the fan did not set

A Follow's hype level SHALL be raisable by the app to a given level only when its hype set by is default or inference and the given level is above its current level in the order Watch, Home, Nearby, Away. A hype level the fan set SHALL never be raisable by the app, and no level is raisable to a lower or equal level.

#### Scenario: Default level below the given level

- **WHEN** the Follow is at Nearby set by default and the given level is Away
- **THEN** the Follow is raisable to Away

#### Scenario: Level the fan set

- **WHEN** the Follow is at Home set by the fan and the given level is Away
- **THEN** the Follow is not raisable

#### Scenario: Given level not higher

- **WHEN** the Follow is at Nearby set by default and the given level is Home
- **THEN** the Follow is not raisable
