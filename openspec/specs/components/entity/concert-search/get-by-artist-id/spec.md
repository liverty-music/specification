# ConcertSearch.GetByArtistID

## Purpose

Returns the ConcertSearch of one Artist.

## Requirements

### Requirement: Get by artist

GetByArtistID SHALL return the Artist's ConcertSearch and SHALL fail with NotFound when the Artist has never been searched.

#### Scenario: Never searched
- **WHEN** the Artist has no ConcertSearch
- **THEN** GetByArtistID fails with NotFound
