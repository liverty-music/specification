## Purpose

This capability provides dedicated infrastructure for artist-related operations, independent of concert management, enabling multi-provider music discovery and metadata aggregation.

## Requirements

### Requirement: Standalone Artist Service
The system SHALL provide a dedicated `ArtistService` that is independent of the `ConcertService` for managing artist-related operations. The service SHALL return Artist entities with populated Fanart data when available.

#### Scenario: Service initialization
- **WHEN** the backend application starts
- **THEN** the `ArtistService` SHALL be registered as a separate RPC handler with its own set of dependencies (repositories, external clients)

#### Scenario: Artist response includes fanart
- **WHEN** any Artist RPC method returns an Artist entity that has Fanart data in the database
- **THEN** the response SHALL include the `fanart` field with best image URLs selected by likes count

#### Scenario: Artist response without fanart
- **WHEN** any Artist RPC method returns an Artist entity without Fanart data
- **THEN** the response SHALL omit the `fanart` field (optional not set)

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
