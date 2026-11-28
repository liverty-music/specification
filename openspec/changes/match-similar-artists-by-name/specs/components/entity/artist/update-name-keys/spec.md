## Purpose

Replaces the names a registered artist is found by, as the music catalog currently lists them.

## ADDED Requirements

### Requirement: UpdateNameKeys replaces the name keys
UpdateNameKeys SHALL take an artist id, the MBID the names were read for and the name keys, set the artist's name_keys to the given keys, change nothing else and announce nothing. When the artist's mbid is no longer the given MBID (Artist.UpdateMBID replaced it after the names were read), it SHALL change nothing and succeed, so another person's names are never stored. It SHALL fail with NotFound when no artist has the id.

#### Scenario: Keys replaced
- **WHEN** UpdateNameKeys is called with the artist's current MBID and new keys
- **THEN** the artist is found by the new keys and no longer by a key that is not among them

#### Scenario: Names of a replaced MBID
- **WHEN** an artist's mbid was replaced from A to B, and UpdateNameKeys is then called with names read for A
- **THEN** the artist keeps B's name keys and UpdateNameKeys succeeds

#### Scenario: Unknown artist
- **WHEN** UpdateNameKeys is called with an id no artist has
- **THEN** it fails with NotFound
