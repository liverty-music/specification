## MODIFIED Requirements

### Requirement: UpdateName replaces the name
UpdateName SHALL take an artist id, the MBID the name was read for and a name, and set the name of the artist with the given id to the given name. When the artist's mbid is no longer the given MBID (Artist.UpdateMBID replaced it after the name was read), it SHALL change nothing and succeed, so another person's name is never stored. It SHALL fail with NotFound when no artist has that id.

#### Scenario: Known artist
- **WHEN** UpdateName is called for a registered artist with its current MBID and a new name
- **THEN** the artist's name is the new name

#### Scenario: Name of a replaced MBID
- **WHEN** an artist's mbid was replaced from A to B, and UpdateName is then called with a name read for A
- **THEN** the artist keeps its name and UpdateName succeeds

#### Scenario: Unknown artist
- **WHEN** UpdateName is called with an id no artist has
- **THEN** UpdateName fails with NotFound and no name changes
