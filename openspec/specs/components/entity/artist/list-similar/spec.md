# Artist.ListSimilar

## Purpose

Looks up, in the music catalog, artists musically similar to a given artist.

## Requirements

### Requirement: ListSimilar returns the catalog's similar artists
ListSimilar SHALL return the artists the music catalog lists as similar to the given artist, identified by its MBID, in the catalog's order, each with a name and, when the catalog knows it, an MBID. When the limit is greater than 0 it SHALL return at most that many artists; when the limit is 0 the catalog's default number applies (TODO(threshold)). When the catalog lists none, ListSimilar SHALL return an empty list.

#### Scenario: Limit given
- **WHEN** ListSimilar is called with a limit of 10
- **THEN** it returns at most 10 artists

#### Scenario: No limit
- **WHEN** ListSimilar is called with a limit of 0
- **THEN** it returns the catalog's default number of artists

#### Scenario: No similar artists
- **WHEN** the catalog lists no similar artist
- **THEN** ListSimilar returns an empty list

### Requirement: ListSimilar reports an unknown artist and catalog failures
ListSimilar SHALL fail with NotFound when the catalog does not recognize the given artist, and with Unavailable when the catalog cannot be reached.

#### Scenario: Artist unknown to the catalog
- **WHEN** the catalog does not recognize the given artist's MBID
- **THEN** ListSimilar fails with NotFound

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ListSimilar fails with Unavailable
