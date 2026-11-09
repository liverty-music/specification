# ArtistUseCase.ListTop

## Purpose

ArtistUseCase.ListTop returns the currently popular artists for a genre tag, else for a country, else worldwide. Each result is registered as an artist so it can be followed.

## Requirements

### Requirement: ListTop returns the chart as registered artists
ArtistUseCase.ListTop SHALL take a country, a tag of at most 50 characters and a limit from 0 to 100, look up the chart with Artist.ListTop, reduce it with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return one registered artist per remaining chart entry in chart order, except the artists whose activity has ended. A limit of 0 means the catalog's default number (TODO(threshold)). The limit applies to the chart lookup, so ListTop may return fewer artists than the limit.

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

### Requirement: ListTop reuses a recent result
ArtistUseCase.ListTop SHALL return the earlier result, without consulting the catalog, when the same country, tag and limit were answered within the last 6 hours, except the artists whose activity has ended by the time of this call.

#### Scenario: Repeated call
- **WHEN** ListTop is called twice with the same country, tag and limit 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** ListTop is called with the same country, tag and limit more than 6 hours after the last such call
- **THEN** the catalog is consulted again

### Requirement: ListTop reports failures
ArtistUseCase.ListTop SHALL return the errors of Artist.ListTop, Artist.ListByMBIDs and Artist.Create unchanged.

#### Scenario: Unknown country
- **WHEN** Artist.ListTop fails with NotFound for the country
- **THEN** ListTop fails with NotFound

#### Scenario: Catalog unavailable
- **WHEN** Artist.ListTop fails with Unavailable
- **THEN** ListTop fails with Unavailable

### Requirement: ListTop leaves out artists whose activity has ended
ArtistUseCase.ListTop SHALL leave out every artist whose activity_ended is true at the time of the call, keeping the chart order of the rest. When it consults the catalog, it SHALL take activity_ended from the artists Artist.ListByMBIDs returns for the registration step, and an artist it registers has activity_ended false. When it reuses an earlier result, it SHALL read the current activity_ended of that result's artists with one Artist.ListByMBIDs call, so an artist whose activity_ended became true after the earlier call is left out.

#### Scenario: Chart lists an ended artist
- **WHEN** the chart for a country lists three registered artists and the second one has activity_ended true
- **THEN** ListTop returns the first and the third artist, in that order

#### Scenario: Artist marked ended after the result was reused
- **WHEN** ListTop answered a country 1 hour ago, and an artist in that answer has had activity_ended true since then
- **THEN** a second call for the same country, tag and limit returns the earlier result without that artist and without a catalog lookup

#### Scenario: Chart artist registered by this call
- **WHEN** a chart artist was not registered before this call
- **THEN** it is returned, since a new artist starts with activity_ended false
