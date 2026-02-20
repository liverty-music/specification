## MODIFIED Requirements

### Requirement: Unified Music Discovery Interface
The system SHALL provide a unified way to search for artists across multiple providers (local database, Last.fm, MusicBrainz). Discovery results SHALL be automatically persisted to the local database to ensure all returned Artist entities have valid database-backed IDs.

#### Scenario: Multi-provider search
- **WHEN** a search request is received
- **THEN** the system SHALL combine and normalize results from multiple sources into a consistent `Artist` entity

#### Scenario: ListTop returns persisted artists
- **WHEN** `ListTop` is called and artists are fetched from the external API
- **THEN** the use case SHALL bulk-insert fetched artists via `ArtistRepository.Create`
- **AND** the use case SHALL return the persisted artists with valid database IDs

#### Scenario: ListSimilar returns persisted artists
- **WHEN** `ListSimilar` is called and similar artists are fetched from the external API
- **THEN** the use case SHALL bulk-insert fetched artists via `ArtistRepository.Create`
- **AND** the use case SHALL return the persisted artists with valid database IDs
