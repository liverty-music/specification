## Purpose

Replaces the names a registered artist is found by, as the music catalog currently lists them.

## ADDED Requirements

### Requirement: UpdateKnownNames replaces the known names
UpdateKnownNames SHALL take an artist id, the MBID the names were read for and the known names, set the artist's known_names to the given known names, change nothing else and announce nothing. When the artist's mbid is no longer the given MBID (Artist.UpdateMBID replaced it after the names were read), it SHALL change nothing and succeed, so another person's names are never stored. It SHALL fail with NotFound when no artist has the id.

#### Scenario: Names replaced
- **WHEN** UpdateKnownNames is called with the artist's current MBID and new names
- **THEN** the artist is found by the new names and no longer by a name that is not among them

#### Scenario: Names of a replaced MBID
- **WHEN** an artist's mbid was replaced from A to B, and UpdateKnownNames is then called with names read for A
- **THEN** the artist keeps B's known names and UpdateKnownNames succeeds

#### Scenario: Unknown artist
- **WHEN** UpdateKnownNames is called with an id no artist has
- **THEN** it fails with NotFound
