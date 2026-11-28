## Purpose

Replaces the names a registered artist is found by, as the music catalog currently lists them.

## ADDED Requirements

### Requirement: UpdateNameKeys replaces the name keys
UpdateNameKeys SHALL set the name_keys of the artist with the given id to the given keys, change nothing else and announce nothing. It SHALL fail with NotFound when no artist has the id.

#### Scenario: Keys replaced
- **WHEN** UpdateNameKeys is called with new keys for a registered artist
- **THEN** the artist is found by the new keys and no longer by a key that is not among them

#### Scenario: Unknown artist
- **WHEN** UpdateNameKeys is called with an id no artist has
- **THEN** it fails with NotFound
