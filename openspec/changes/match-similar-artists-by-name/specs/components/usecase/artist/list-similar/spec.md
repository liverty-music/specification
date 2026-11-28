## MODIFIED Requirements

### Requirement: ListSimilar returns the catalog's similar artists as registered artists
ArtistUseCase.ListSimilar SHALL take an artist id and a limit from 0 to 50, get the seed artist with Artist.Get, look up similar artists with Artist.ListSimilar (which identifies the seed by its listening_mbid) and a limit of 50 regardless of the requested limit, reduce the results with an MBID with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs (under their mbid or listening_mbid), register the rest with Artist.Create with the result's MBID as both its listening MBID and its MBID and mbid_status Unverified, match the results without an MBID to registered artists as "ListSimilar matches results without an MBID by name" states, and return the first `limit` registered artists in the catalog's order among those offered to fans, listing an artist once when several results resolve to it. A limit of 0 returns every remaining result of the 50-artist lookup that is offered to fans.

#### Scenario: Known and new similar artists
- **WHEN** the catalog lists a registered Verified artist and an unregistered artist as similar
- **THEN** ListSimilar registers only the unregistered one, Unverified, and returns only the registered Verified one

#### Scenario: Result without MBID
- **WHEN** the catalog lists a similar artist without an MBID whose name no registered artist has
- **THEN** that result is neither registered nor returned

#### Scenario: Limit given
- **WHEN** ListSimilar is called with a limit of 10
- **THEN** Artist.ListSimilar is asked for 50 artists
- **AND** at most 10 artists are returned, the first 10 in the catalog's order

#### Scenario: Limit of zero
- **WHEN** ListSimilar is called with a limit of 0 and the catalog lists 42 similar artists that are registered and offered to fans
- **THEN** all 42 artists are returned

#### Scenario: No similar artists
- **WHEN** the catalog lists no similar artist
- **THEN** ListSimilar returns an empty list

#### Scenario: Result under a replaced MBID
- **WHEN** the catalog lists MBID A as similar and a registered Verified artist has listening_mbid A and mbid B
- **THEN** ListSimilar returns that artist and registers nothing

#### Scenario: Seed whose MBID was corrected
- **WHEN** ListSimilar is called for an artist with listening_mbid A and mbid B
- **THEN** the similar artists are looked up for A

## ADDED Requirements

### Requirement: ListSimilar matches results without an MBID by name
After registering the results with an MBID, ArtistUseCase.ListSimilar SHALL look the names of all results without an MBID up with one Artist.ListByKnownNames call. A result SHALL stand for a registered artist only when exactly one of the returned artists has its name, counting artists that are not offered to fans, and that artist is not the seed. The artist takes the result's position in the catalog's order and is listed once. A result without an MBID SHALL never be registered. When there is no result without an MBID, Artist.ListByKnownNames is not called.

#### Scenario: Registered artist listed by a romanized name
- **WHEN** the catalog lists `Yorushika` without an MBID and exactly one registered artist, offered to fans, has that name as an alias
- **THEN** ListSimilar returns that artist at the result's position and registers nothing

#### Scenario: Two registered artists have the name
- **WHEN** the catalog lists `tomoo` without an MBID and two registered artists have that name, one of them not offered to fans
- **THEN** neither is returned for that result

#### Scenario: Matched artist not offered
- **WHEN** the only registered artist with the result's name is not offered to fans
- **THEN** it is not returned

#### Scenario: Same artist listed twice
- **WHEN** the catalog lists an artist once with its MBID and once by another of its names without an MBID
- **THEN** ListSimilar returns it once, at its first position

#### Scenario: Match is the seed
- **WHEN** a result without an MBID has a name of the seed artist only
- **THEN** the seed is not returned

#### Scenario: Name lookup fails
- **WHEN** Artist.ListByKnownNames fails with Unavailable
- **THEN** ListSimilar fails with Unavailable
