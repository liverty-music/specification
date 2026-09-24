# Artist.ResolveImages

## Purpose

Looks up the community-curated images of the artist with a given MBID in the image catalog.

## Requirements

### Requirement: ResolveImages returns the artist's images or none
ResolveImages SHALL return the image catalog's images for the MBID, grouped by kind, with each image's id, URL, like count and language; a kind the catalog has no image of SHALL be empty. When the catalog has no entry for the MBID, ResolveImages SHALL return no fanart and no error.

#### Scenario: All kinds available
- **WHEN** the catalog has images of every kind for the MBID
- **THEN** ResolveImages returns fanart with images in every kind

#### Scenario: Some kinds available
- **WHEN** the catalog has only artist_thumb and hd_music_logo images for the MBID
- **THEN** ResolveImages returns fanart with those two kinds filled and the other kinds empty

#### Scenario: No entry
- **WHEN** the catalog has no entry for the MBID
- **THEN** ResolveImages returns no fanart and no error

### Requirement: ResolveImages reports catalog failures
ResolveImages SHALL fail with Unavailable when the image catalog cannot be reached or is rate-limiting after retries, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the image catalog cannot be reached
- **THEN** ResolveImages fails with Unavailable
