# Artist.GetArtist

## Purpose

Looks up an MBID in the music catalog and returns the catalog's canonical name and MBID for it.

## Requirements

### Requirement: GetArtist returns the canonical artist
GetArtist SHALL return the catalog's canonical name and MBID for the given MBID. It SHALL fail with NotFound when the catalog has no artist for the MBID and with Unavailable when the catalog cannot be reached.

#### Scenario: Known MBID
- **WHEN** GetArtist is called with an MBID the catalog knows
- **THEN** it returns the catalog's name and MBID for that artist

#### Scenario: Unknown MBID
- **WHEN** GetArtist is called with an MBID the catalog does not know
- **THEN** GetArtist fails with NotFound

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** GetArtist fails with Unavailable
