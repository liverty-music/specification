# Artist.Search

## Purpose

Looks up artists by name in the music catalog.

## Requirements

### Requirement: Search returns the catalog's name matches
Search SHALL return the artists the music catalog matches to the query, in the catalog's order, each with a name and, when the catalog knows it, an MBID. The results are not registered artists. When the catalog has no match, Search SHALL return an empty list.

#### Scenario: Matches found
- **WHEN** Search is called with a query the catalog matches
- **THEN** it returns the matching artists in the catalog's order

#### Scenario: Match without MBID
- **WHEN** the catalog matches an artist it has no MBID for
- **THEN** that result has a name and no MBID

#### Scenario: No match
- **WHEN** the catalog matches nothing
- **THEN** Search returns an empty list

### Requirement: Search reports catalog failures
Search SHALL fail with Unavailable when the catalog cannot be reached or is rate-limiting after retries, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** Search fails with Unavailable
