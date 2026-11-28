## RENAMED Requirements

- FROM: `### Requirement: ListTop leaves out artists whose activity has ended`
- TO: `### Requirement: ListTop leaves out artists not offered to fans`

## MODIFIED Requirements

### Requirement: ListTop returns the chart as registered artists
ArtistUseCase.ListTop SHALL take a country, a tag of at most 50 characters and a limit from 0 to 100, look up the chart with Artist.ListTop, reduce it with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs (under their mbid or listening_mbid), register the rest with Artist.Create with the entry's MBID as both its listening MBID and its MBID and mbid_status Unverified, and return one registered artist per remaining chart entry in chart order, only the artists offered to fans, listing an artist once when several entries resolve to it. A limit of 0 means the catalog's default number (TODO(threshold)). The limit applies to the chart lookup, so ListTop may return fewer artists than the limit.

#### Scenario: First call for a country
- **WHEN** ListTop is called for a country whose chart artists are not registered
- **THEN** each chart artist with an MBID is registered Unverified, and none of them is returned by this call

#### Scenario: Repeated call keeps identities
- **WHEN** ListTop is called twice for the same country
- **THEN** both calls return the same artist for each MBID

#### Scenario: Chart artist already registered
- **WHEN** a chart artist's MBID is already registered
- **THEN** the registered artist is returned when it is offered to fans, and no second artist is registered

#### Scenario: Chart artist without MBID
- **WHEN** a chart entry has no MBID
- **THEN** it is neither registered nor returned

#### Scenario: Empty chart
- **WHEN** the chart has no artists
- **THEN** ListTop returns an empty list

#### Scenario: Chart artist under a replaced MBID
- **WHEN** a chart entry has MBID A and a registered Verified artist has listening_mbid A and mbid B
- **THEN** ListTop returns that artist and registers nothing

### Requirement: ListTop leaves out artists not offered to fans
ArtistUseCase.ListTop SHALL leave out every artist that is not offered to fans at the time of the call (mbid_status other than Verified, or activity_ended true), keeping the chart order of the rest. When it consults the catalog, it SHALL take mbid_status and activity_ended from the artists Artist.ListByMBIDs returns for the registration step, and an artist it registers is Unverified. When it reuses an earlier result, it SHALL read the current mbid_status and activity_ended of that result's artists with one Artist.ListByMBIDs call, so an artist whose activity_ended became true after the earlier call is left out.

#### Scenario: Chart lists an ended artist
- **WHEN** the chart for a country lists three registered Verified artists and the second one has activity_ended true
- **THEN** ListTop returns the first and the third artist, in that order

#### Scenario: Artist marked ended after the result was reused
- **WHEN** ListTop answered a country 1 hour ago, and an artist in that answer has had activity_ended true since then
- **THEN** a second call for the same country, tag and limit returns the earlier result without that artist and without a catalog lookup

#### Scenario: Chart artist registered by this call
- **WHEN** a chart artist was not registered before this call
- **THEN** it is not returned, since a new artist starts Unverified

#### Scenario: Chart artist verified after the result
- **WHEN** a chart artist registered by a call 1 hour ago has become Verified since then, and ListTop reuses that call's result
- **THEN** the artist is returned
