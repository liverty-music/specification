# Artist.FilterArtistsByMBID

## Purpose

Reduces a list of artists to those with an MBID, one per MBID, keeping the input order.

## Requirements

### Requirement: FilterArtistsByMBID drops missing and repeated MBIDs
FilterArtistsByMBID SHALL drop every artist without an MBID, keep only the first artist for each MBID, and keep the input order of the artists it keeps.

#### Scenario: Mixed MBIDs
- **WHEN** the input has artists with MBIDs "abc", none, "def" and "abc"
- **THEN** the result has the artists with MBIDs "abc" and "def", in that order, and the "abc" artist is the first one

#### Scenario: No MBIDs
- **WHEN** no input artist has an MBID
- **THEN** the result is empty

#### Scenario: Unique MBIDs
- **WHEN** every input artist has a different MBID
- **THEN** the result is the input unchanged

#### Scenario: Empty input
- **WHEN** the input is empty
- **THEN** the result is empty
