## ADDED Requirements

### Requirement: GetArtist returns the catalog's aliases
GetArtist SHALL return, with the canonical artist, the name keys of the catalog's name and of every alias the catalog lists for it.

#### Scenario: Artist with aliases
- **WHEN** GetArtist is called for an artist the catalog names `ヨルシカ` with the alias `Yorushika`
- **THEN** the returned artist has both names

#### Scenario: Artist without aliases
- **WHEN** the catalog lists no alias for the artist
- **THEN** the returned artist's name keys hold only its name's key
