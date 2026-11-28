## MODIFIED Requirements

### Requirement: ListTop returns the chart as registered artists
ArtistUseCase.ListTop SHALL take a country, a tag of at most 50 characters and a limit from 0 to 100, look up the chart with Artist.ListTop, reduce it with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return one registered artist per remaining chart entry in chart order, except the artists whose activity has ended, listing an artist once when several entries resolve to it. An entry whose MBID is one an artist was corrected from SHALL resolve to the corrected artist and register nothing. A limit of 0 means the catalog's default number (TODO(threshold)). The limit applies to the chart lookup, so ListTop may return fewer artists than the limit.

#### Scenario: First call for a country
- **WHEN** ListTop is called for a country whose chart artists are not registered
- **THEN** each chart artist with an MBID is registered and returned in chart order

#### Scenario: Repeated call keeps identities
- **WHEN** ListTop is called twice for the same country
- **THEN** both calls return the same artist for each MBID

#### Scenario: Chart artist already registered
- **WHEN** a chart artist's MBID is already registered
- **THEN** the registered artist is returned and no second artist is registered

#### Scenario: Chart artist without MBID
- **WHEN** a chart entry has no MBID
- **THEN** it is neither registered nor returned

#### Scenario: Empty chart
- **WHEN** the chart has no artists
- **THEN** ListTop returns an empty list

#### Scenario: Chart artist under a replaced MBID
- **WHEN** a chart entry has MBID A and an artist was corrected from A to B
- **THEN** ListTop returns that artist and registers nothing
