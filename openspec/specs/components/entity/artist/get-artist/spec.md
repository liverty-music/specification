# Artist.GetArtist

## Purpose

Looks up an MBID in the music catalog and returns the catalog's canonical name and MBID for it, and whether the catalog marks the artist's activity as ended.

## Requirements

### Requirement: GetArtist returns the canonical artist
GetArtist SHALL return the catalog's canonical name and MBID for the given MBID, and whether the catalog marks the artist's activity as ended: true when the catalog records that the group dissolved or the solo artist died, whether or not it records the end date; false when it records no end. It SHALL fail with NotFound when the catalog has no artist for the MBID and with Unavailable when the catalog cannot be reached.

#### Scenario: Known MBID
- **WHEN** GetArtist is called with an MBID the catalog knows
- **THEN** it returns the catalog's name and MBID for that artist

#### Scenario: Ended activity
- **WHEN** the catalog records that the artist's activity ended in 2016
- **THEN** GetArtist returns activity ended true

#### Scenario: Ended activity without an end date
- **WHEN** the catalog records that the artist's activity ended but gives no end date
- **THEN** GetArtist returns activity ended true

#### Scenario: Activity not ended
- **WHEN** the catalog records a start date and no end for the artist
- **THEN** GetArtist returns activity ended false

#### Scenario: Unknown MBID
- **WHEN** GetArtist is called with an MBID the catalog does not know
- **THEN** GetArtist fails with NotFound

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** GetArtist fails with Unavailable
