# ArtistUseCase.ListSimilar

## Purpose

ArtistUseCase.ListSimilar returns artists musically similar to a given artist, each registered as an artist so it can be followed, up to a caller-chosen number.

## Requirements

### Requirement: ListSimilar returns the catalog's similar artists as registered artists
ArtistUseCase.ListSimilar SHALL take an artist id and a limit from 0 to 100, get the seed artist with Artist.Get, look up similar artists with Artist.ListSimilar and the limit, reduce them with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs, register the rest with Artist.Create, and return one registered artist per remaining result in the catalog's order. A limit of 0 means the catalog's default number (TODO(threshold)).

#### Scenario: Known and new similar artists
- **WHEN** the catalog lists a registered artist and an unregistered artist as similar
- **THEN** ListSimilar registers only the unregistered one and returns both in the catalog's order

#### Scenario: Result without MBID
- **WHEN** the catalog lists a similar artist without an MBID
- **THEN** that result is neither registered nor returned

#### Scenario: Limit given
- **WHEN** ListSimilar is called with a limit of 10
- **THEN** at most 10 artists are returned

#### Scenario: No similar artists
- **WHEN** the catalog lists no similar artist
- **THEN** ListSimilar returns an empty list

### Requirement: ListSimilar announces newly registered artists
For each artist that Artist.Create returns, ArtistUseCase.ListSimilar SHALL announce that the artist was created, with its id, name and MBID. A failed announcement SHALL NOT fail the call.

#### Scenario: New artist registered
- **WHEN** ListSimilar registers an artist
- **THEN** an artist-created announcement for it is made

### Requirement: ListSimilar reuses a recent result
ArtistUseCase.ListSimilar SHALL return the earlier result, without looking up the seed or consulting the catalog, when the same artist id and limit were answered within the last 1 hour.

#### Scenario: Repeated call
- **WHEN** ListSimilar is called twice with the same artist id and limit 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

### Requirement: ListSimilar reports failures
ArtistUseCase.ListSimilar SHALL return the errors of Artist.Get, Artist.ListSimilar, Artist.ListByMBIDs and Artist.Create unchanged.

#### Scenario: Unknown seed artist
- **WHEN** no artist has the given id
- **THEN** ListSimilar fails with NotFound

#### Scenario: Seed unknown to the catalog
- **WHEN** Artist.ListSimilar fails with NotFound
- **THEN** ListSimilar fails with NotFound

#### Scenario: Catalog unavailable
- **WHEN** Artist.ListSimilar fails with Unavailable
- **THEN** ListSimilar fails with Unavailable
