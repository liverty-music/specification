## MODIFIED Requirements

### Requirement: Follow creates the fan's Follow of the artist

Follow SHALL create the fan's Follow of the artist through Follow.Follow and succeed once it is stored. When the Follow cannot be stored, Follow SHALL do nothing else and fail: with Unavailable when Follow.Follow fails with Unavailable (its announcement cannot be recorded, so the call can be retried), and with Internal otherwise, including when the artist does not exist.

#### Scenario: Fan follows a new artist

- **WHEN** a fan follows an artist they do not follow
- **THEN** the Follow is stored and Follow succeeds

#### Scenario: Announcement cannot be recorded

- **WHEN** Follow.Follow fails with Unavailable
- **THEN** Follow fails with Unavailable and no background work is started

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** Follow fails with Internal and no background work is started

### Requirement: A repeat follow changes nothing

When the fan already follows the artist, Follow SHALL succeed without changing the Follow or its hype level and without starting any background work.

#### Scenario: Fan follows the same artist twice

- **WHEN** a fan who follows an artist at Away follows it again
- **THEN** Follow succeeds, the hype level stays Away, and no background work is started

## REMOVED Requirements

### Requirement: Follow announces the new follow
**Reason**: Follow.Follow announces a new Follow together with storing it (components/entity/follow/follow), so the usecase no longer announces.
**Migration**: ConcertUseCase.SearchNewConcertsOnFirstFollow and product analytics receive the new follow from Follow.Follow's announcement. A failure to announce now fails Follow with Unavailable and stores no Follow, so a stored follow is always announced and the artist is no longer left to the daily concert search.
