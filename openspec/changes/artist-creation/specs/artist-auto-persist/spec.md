## Purpose

This capability ensures that artists discovered from external sources (Last.fm) are automatically persisted to the local database during ListTop and ListSimilar operations, guaranteeing every returned Artist entity has a valid database-backed ID.

## ADDED Requirements

### Requirement: Auto-persist external artists during ListTop
The system SHALL automatically persist artists retrieved from external discovery APIs to the local database before returning them from the ListTop use case.

#### Scenario: First call for a country with no cached artists
- **WHEN** `ListTop` is called for a country and the cache is empty
- **THEN** the system SHALL fetch artists from the external API
- **AND** the system SHALL bulk-insert all fetched artists into the `artists` table using MBID-based deduplication
- **AND** the system SHALL return all artists with valid database-assigned `id` fields

#### Scenario: Repeated call returns artists with stable IDs
- **WHEN** `ListTop` is called twice for the same country
- **THEN** the artists returned in both calls SHALL have the same `id` values for matching MBIDs

#### Scenario: External artist already exists in database
- **WHEN** an artist returned by the external API already exists in the local database (matching MBID)
- **THEN** the system SHALL return the existing database record without creating a duplicate

### Requirement: Auto-persist external artists during ListSimilar
The system SHALL automatically persist similar artists retrieved from external discovery APIs to the local database before returning them from the ListSimilar use case.

#### Scenario: Similar artists persisted on discovery
- **WHEN** `ListSimilar` is called for a seed artist
- **THEN** the system SHALL fetch similar artists from the external API
- **AND** the system SHALL bulk-insert all fetched artists into the `artists` table using MBID-based deduplication
- **AND** the system SHALL return all similar artists with valid database-assigned `id` fields

### Requirement: Handle artists without MBID
The system SHALL gracefully handle artists returned by external APIs that lack a MusicBrainz ID.

#### Scenario: Artist with empty MBID
- **WHEN** an external API returns an artist with an empty MBID
- **THEN** the system SHALL insert the artist as a new record (no deduplication possible)
- **AND** the artist SHALL receive a valid database-assigned `id`
