# Spec Delta

## MODIFIED Requirements

### Requirement: A repeat follow changes nothing

When the fan already follows the artist, Follow SHALL succeed without changing the Follow or its hype level, without announcing the follow again and without starting any background work.

#### Scenario: Fan follows the same artist twice

- **WHEN** a fan who follows an artist at Away follows it again
- **THEN** Follow succeeds, the hype level stays Away, and the follow is not announced a second time
