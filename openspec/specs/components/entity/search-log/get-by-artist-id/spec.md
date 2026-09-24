# SearchLog.GetByArtistID

## Purpose

Returns the SearchLog of one Artist.

## Requirements

### Requirement: Get by artist

GetByArtistID SHALL return the Artist's SearchLog and SHALL fail with NotFound when the Artist has never been searched.

#### Scenario: Never searched
- **WHEN** the Artist has no SearchLog
- **THEN** GetByArtistID fails with NotFound
