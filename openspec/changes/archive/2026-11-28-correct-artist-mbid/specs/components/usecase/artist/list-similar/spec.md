## MODIFIED Requirements

### Requirement: ListSimilar returns the catalog's similar artists as registered artists
ArtistUseCase.ListSimilar SHALL take an artist id and a limit from 0 to 50, get the seed artist with Artist.Get, look up similar artists with Artist.ListSimilar and a limit of 50 regardless of the requested limit, reduce them with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return the first `limit` registered artists in the catalog's order among those whose activity has not ended, listing an artist once when several results resolve to it. A result whose MBID is one an artist was corrected from SHALL resolve to the corrected artist and register nothing. A limit of 0 returns every remaining result of the 50-artist lookup whose activity has not ended.

#### Scenario: Known and new similar artists
- **WHEN** the catalog lists a registered artist and an unregistered artist as similar
- **THEN** ListSimilar registers only the unregistered one and returns both in the catalog's order

#### Scenario: Result without MBID
- **WHEN** the catalog lists a similar artist without an MBID
- **THEN** that result is neither registered nor returned

#### Scenario: Limit given
- **WHEN** ListSimilar is called with a limit of 10
- **THEN** Artist.ListSimilar is asked for 50 artists
- **AND** at most 10 artists are returned, the first 10 in the catalog's order

#### Scenario: Limit of zero
- **WHEN** ListSimilar is called with a limit of 0 and the catalog lists 42 similar artists with an MBID
- **THEN** all 42 artists are returned

#### Scenario: No similar artists
- **WHEN** the catalog lists no similar artist
- **THEN** ListSimilar returns an empty list

#### Scenario: Result under a replaced MBID
- **WHEN** the catalog lists MBID A as similar and an artist was corrected from A to B
- **THEN** ListSimilar returns that artist and registers nothing
