## MODIFIED Requirements

### Requirement: Search returns the catalog's matches as registered artists
ArtistUseCase.Search SHALL look the query up with Artist.Search, reduce the matches with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return one registered artist per remaining match in the catalog's order, listing an artist once when several matches resolve to it. A match whose MBID is one an artist was corrected from SHALL resolve to the corrected artist and register nothing.

#### Scenario: Known and new matches
- **WHEN** the catalog matches a registered artist and an unregistered artist, in that order
- **THEN** Search registers only the unregistered one and returns both registered artists in that order

#### Scenario: Match without MBID
- **WHEN** the catalog matches an artist without an MBID
- **THEN** that match is neither registered nor returned

#### Scenario: No match with an MBID
- **WHEN** no catalog match has an MBID
- **THEN** Search fails with NotFound and registers nothing

#### Scenario: Match under a replaced MBID
- **WHEN** the catalog matches MBID A and an artist was corrected from A to B
- **THEN** Search returns that artist and registers nothing

#### Scenario: Two matches of one artist
- **WHEN** the catalog matches MBIDs A and B of one registered artist
- **THEN** Search returns that artist once
