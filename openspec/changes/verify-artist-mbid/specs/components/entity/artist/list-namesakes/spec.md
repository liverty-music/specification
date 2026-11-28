## Purpose

Looks up, in the music catalog, every artist whose name equals a given name, so an artist's MBID can be checked against its namesakes.

## ADDED Requirements

### Requirement: ListNamesakes returns the catalog's artists of exactly that name
ListNamesakes SHALL return, as CatalogArtists without official_site_url, the music catalog's artists whose name equals the given name ignoring letter case, in the catalog's order, each once. An artist whose name only resembles the given name SHALL not be returned. When the catalog has no such artist, ListNamesakes SHALL return an empty list.

#### Scenario: Two artists share the name
- **WHEN** ListNamesakes is called with "Penthouse" and the catalog has a Japanese band and a UK band named "Penthouse"
- **THEN** both are returned, each with its MBID, country, life span and disambiguation

#### Scenario: Different letter case
- **WHEN** ListNamesakes is called with "sumika" and the catalog records an artist named "Sumika"
- **THEN** that artist is returned

#### Scenario: Similar name only
- **WHEN** ListNamesakes is called with "Ado" and the catalog has artists named "Ado" and "Adore"
- **THEN** only the artist named "Ado" is returned

#### Scenario: No artist of that name
- **WHEN** the catalog has no artist with the given name
- **THEN** ListNamesakes returns an empty list

### Requirement: ListNamesakes reports catalog failures
ListNamesakes SHALL fail with Unavailable when the catalog cannot be reached or is rate-limiting after retries, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ListNamesakes fails with Unavailable
