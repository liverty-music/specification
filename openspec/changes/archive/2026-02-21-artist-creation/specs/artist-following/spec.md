## MODIFIED Requirements

### Requirement: Persist User Follow Actions
The system SHALL persist user follow and unfollow actions for specific artists in a relational database. The frontend SHALL call the backend `ArtistService.Follow` RPC when a user taps an artist bubble.

#### Scenario: Successfully following an artist
- **WHEN** a user with a valid ID requests to follow an artist with a valid MBID
- **THEN** the system SHALL create a record in the `followed_artists` table linking the user to the artist

#### Scenario: Frontend calls Follow RPC on bubble tap
- **WHEN** a user taps an artist bubble in the discovery UI
- **THEN** the frontend SHALL call `ArtistService.Follow` RPC with the artist's database-assigned `id`
- **AND** the frontend SHALL update local state immediately without waiting for the RPC response
- **AND** any RPC error SHALL be logged but SHALL NOT block the UI interaction
