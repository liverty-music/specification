## MODIFIED Requirements

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
