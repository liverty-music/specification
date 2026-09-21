# List Similar

## Purpose

Returns artists similar to a given artist, automatically persisting any externally discovered artists so every result has a stable database-backed identity, with a caller-controlled result limit.

## Requirements

### Requirement: Auto-persist external artists during ListSimilar
The system SHALL automatically persist similar artists retrieved from external discovery APIs to the local database before returning them from the ListSimilar use case.

#### Scenario: Similar artists persisted on discovery
- **WHEN** `ListSimilar` is called for a seed artist
- **THEN** the system SHALL fetch similar artists from the external API
- **AND** the system SHALL bulk-insert all fetched artists into the `artists` table using MBID-based deduplication
- **AND** the system SHALL return all similar artists with valid database-assigned `id` fields

### Requirement: ListSimilar and ListTop limit parameter
The `ArtistService.ListSimilar` and `ArtistService.ListTop` RPCs SHALL accept an optional `limit` parameter to control the maximum number of results.

#### Scenario: Limit parameter provided
- **WHEN** a client sends `ListSimilarRequest` or `ListTopRequest` with `limit > 0`
- **THEN** the server SHALL return at most `limit` artists
- **AND** the limit SHALL be validated as an integer between 0 and 100

#### Scenario: Limit parameter omitted or zero
- **WHEN** a client sends a request with `limit = 0` or omits the field
- **THEN** the server SHALL use its default limit
