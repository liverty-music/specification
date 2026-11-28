## MODIFIED Requirements

### Requirement: UpdateActivityEnded sets the activity status
UpdateActivityEnded SHALL take an artist id, the MBID the status was read for and a value, and set the activity_ended of the artist with the given id to the value, true or false. When the artist's mbid is no longer the given MBID (Artist.UpdateMBID replaced it after the status was read), it SHALL change nothing and succeed, so another person's status is never stored. It SHALL fail with NotFound when no artist has the id. Setting the value the artist already has SHALL succeed and change nothing.

#### Scenario: Activity ended
- **WHEN** UpdateActivityEnded is called with the artist's current MBID and true for an artist whose activity_ended is false
- **THEN** the artist's activity_ended is true

#### Scenario: Activity resumed in the catalog
- **WHEN** UpdateActivityEnded is called with the artist's current MBID and false for an artist whose activity_ended is true
- **THEN** the artist's activity_ended is false

#### Scenario: Same value
- **WHEN** UpdateActivityEnded is called with the value the artist already has
- **THEN** it succeeds and the artist is unchanged

#### Scenario: Status of a replaced MBID
- **WHEN** an artist's mbid was replaced from A to B, and UpdateActivityEnded is then called with a status read for A
- **THEN** the artist keeps its activity_ended and UpdateActivityEnded succeeds

#### Scenario: Unknown artist
- **WHEN** UpdateActivityEnded is called with an id no artist has
- **THEN** UpdateActivityEnded fails with NotFound
