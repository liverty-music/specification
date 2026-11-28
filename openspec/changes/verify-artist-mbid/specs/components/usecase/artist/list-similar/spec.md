## RENAMED Requirements

- FROM: `### Requirement: ListSimilar leaves out artists whose activity has ended`
- TO: `### Requirement: ListSimilar leaves out artists not offered to fans`

## MODIFIED Requirements

### Requirement: ListSimilar returns the catalog's similar artists as registered artists
ArtistUseCase.ListSimilar SHALL take an artist id and a limit from 0 to 50, get the seed artist with Artist.Get, look up similar artists with Artist.ListSimilar (which identifies the seed by its listening_mbid) and a limit of 50 regardless of the requested limit, reduce them with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs (under their mbid or listening_mbid), register the rest with Artist.Create with the result's MBID as both its listening MBID and its MBID and mbid_status Unverified, and return the first `limit` registered artists in the catalog's order among those offered to fans, listing an artist once when several results resolve to it. A limit of 0 returns every remaining result of the 50-artist lookup that is offered to fans.

#### Scenario: Known and new similar artists
- **WHEN** the catalog lists a registered Verified artist and an unregistered artist as similar
- **THEN** ListSimilar registers only the unregistered one, Unverified, and returns only the registered Verified one

#### Scenario: Result without MBID
- **WHEN** the catalog lists a similar artist without an MBID
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

### Requirement: ListSimilar reuses a recent result
ArtistUseCase.ListSimilar SHALL return the earlier result, without the artists not offered to fans by the time of this call and then cut to the requested limit, without looking up the seed or consulting the catalog, when the same artist id was answered within the last 6 hours, whatever limit either call used.

#### Scenario: Repeated call
- **WHEN** ListSimilar is called twice with the same artist id and limit 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Repeated call with a different limit
- **WHEN** ListSimilar is called for an artist with a limit of 30 and, 1 hour later, for the same artist with a limit of 10
- **THEN** the second call returns the first 10 artists of the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** ListSimilar is called for an artist more than 6 hours after the last call for that artist
- **THEN** the catalog is consulted again

### Requirement: ListSimilar leaves out artists not offered to fans
ArtistUseCase.ListSimilar SHALL leave out every similar artist that is not offered to fans at the time of the call (mbid_status other than Verified, or activity_ended true), before it cuts the result to the requested limit. The seed artist's own mbid_status and activity_ended SHALL NOT matter: any registered seed gets its similar artists. When it consults the catalog, it SHALL take mbid_status and activity_ended from the artists Artist.ListByMBIDs returns for the registration step, and an artist it registers is Unverified. When it reuses an earlier result for the same artist id, it SHALL read the current mbid_status and activity_ended of that result's artists with one Artist.ListByMBIDs call.

#### Scenario: Ended artist within the limit
- **WHEN** ListSimilar is called with a limit of 10 and the third of the catalog's similar artists, all registered and Verified, has activity_ended true
- **THEN** 10 artists are returned: the first, the second, and the fourth to the eleventh

#### Scenario: Artist marked ended after the result was reused
- **WHEN** ListSimilar answered an artist 1 hour ago, and a similar artist in that answer has had activity_ended true since then
- **THEN** a second call for the same artist returns the earlier result without that artist and without a catalog lookup

#### Scenario: Similar artist verified after the result
- **WHEN** a similar artist registered by a call 1 hour ago has become Verified since then, and ListSimilar reuses that call's result
- **THEN** the artist is returned

#### Scenario: Seed artist whose activity has ended
- **WHEN** ListSimilar is called for an artist whose own activity_ended is true
- **THEN** it returns that artist's similar artists as for any other artist
