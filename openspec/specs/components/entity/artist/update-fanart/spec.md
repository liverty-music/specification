# Artist.UpdateFanart

## Purpose

Records the result of an image check for an artist: its images, or none, and the time of the check.

## Requirements

### Requirement: UpdateFanart replaces the images and the check time
UpdateFanart SHALL replace the artist's fanart with the given fanart and set its fanart_sync_time to the given time. When no fanart is given, the artist SHALL be left with no fanart, removing any earlier images, and the check time SHALL still be set. It SHALL fail with NotFound when no artist has the given id.

#### Scenario: Images given
- **WHEN** UpdateFanart is called with fanart and a time
- **THEN** the artist's fanart is the given fanart and its fanart_sync_time is the given time

#### Scenario: No images given
- **WHEN** UpdateFanart is called without fanart for an artist that had images
- **THEN** the artist has no fanart and its fanart_sync_time is the given time

#### Scenario: Unknown artist
- **WHEN** UpdateFanart is called with an id no artist has
- **THEN** UpdateFanart fails with NotFound
