# ArtistUseCase.Search

## Purpose

ArtistUseCase.Search finds artists whose names match a fan's query in the music catalog. Each result is returned as a registered artist, so any result can be followed.

## Requirements

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

### Requirement: Search reuses a recent result
ArtistUseCase.Search SHALL return the earlier result, without consulting the catalog or registering anything, when the same query was answered within the last 6 hours.

#### Scenario: Repeated query
- **WHEN** Search is called twice with the same query 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** Search is called with the same query more than 6 hours after the last such call
- **THEN** the catalog is consulted again

### Requirement: Search reports failures
ArtistUseCase.Search SHALL return the errors of Artist.Search, Artist.ListByMBIDs, and Artist.Create unchanged, preserving each port's failure code rather than replacing it with Internal.

#### Scenario: Catalog unavailable
- **WHEN** Artist.Search fails with Unavailable
- **THEN** Search fails with Unavailable

#### Scenario: Catalog rate-limited
- **WHEN** Artist.Search fails with ResourceExhausted
- **THEN** Search fails with ResourceExhausted

#### Scenario: Catalog request timed out
- **WHEN** Artist.Search fails with DeadlineExceeded
- **THEN** Search fails with DeadlineExceeded
