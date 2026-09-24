# ArtistUseCase.ListTop

## Purpose

ArtistUseCase.ListTop returns the currently popular artists for a genre tag, else for a country, else worldwide. Each result is registered as an artist so it can be followed.

## Requirements

### Requirement: ListTop returns the chart as registered artists
ArtistUseCase.ListTop SHALL take a country, a tag of at most 50 characters and a limit from 0 to 100, look up the chart with Artist.ListTop, reduce it with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return one registered artist per remaining chart entry in chart order. A limit of 0 means the catalog's default number (TODO(threshold)).

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

### Requirement: ListTop announces newly registered artists
For each artist that Artist.Create returns, ArtistUseCase.ListTop SHALL announce that the artist was created, with its id, name and MBID. A failed announcement SHALL NOT fail the call.

#### Scenario: New artist registered
- **WHEN** ListTop registers an artist
- **THEN** an artist-created announcement for it is made

### Requirement: ListTop reuses a recent result
ArtistUseCase.ListTop SHALL return the earlier result, without consulting the catalog, when the same country, tag and limit were answered within the last 1 hour.

#### Scenario: Repeated call
- **WHEN** ListTop is called twice with the same country, tag and limit 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

### Requirement: ListTop reports failures
ArtistUseCase.ListTop SHALL return the errors of Artist.ListTop, Artist.ListByMBIDs and Artist.Create unchanged.

#### Scenario: Unknown country
- **WHEN** Artist.ListTop fails with NotFound for the country
- **THEN** ListTop fails with NotFound

#### Scenario: Catalog unavailable
- **WHEN** Artist.ListTop fails with Unavailable
- **THEN** ListTop fails with Unavailable
