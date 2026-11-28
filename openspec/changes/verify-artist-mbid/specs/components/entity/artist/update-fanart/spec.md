## MODIFIED Requirements

### Requirement: UpdateFanart replaces the images and the check time
UpdateFanart SHALL take an artist id, the MBID the images were resolved for, the images or none, and a time. It SHALL replace the artist's fanart with the given fanart and set its fanart_sync_time to the given time. When no fanart is given, the artist SHALL be left with no fanart, removing any earlier images, and the check time SHALL still be set. When the artist's mbid is no longer the given MBID (Artist.UpdateMBID replaced it after the images were resolved), UpdateFanart SHALL change nothing and succeed, so another person's images are never stored. It SHALL fail with NotFound when no artist has the given id.

#### Scenario: Images given
- **WHEN** UpdateFanart is called with fanart and a time
- **THEN** the artist's fanart is the given fanart and its fanart_sync_time is the given time

#### Scenario: No images given
- **WHEN** UpdateFanart is called without fanart for an artist that had images
- **THEN** the artist has no fanart and its fanart_sync_time is the given time

#### Scenario: Images of a replaced MBID
- **WHEN** an artist's mbid was replaced from A to B, and UpdateFanart is then called with images resolved for A
- **THEN** the artist keeps no fanart and no fanart_sync_time, and UpdateFanart succeeds

#### Scenario: Unknown artist
- **WHEN** UpdateFanart is called with an id no artist has
- **THEN** UpdateFanart fails with NotFound
