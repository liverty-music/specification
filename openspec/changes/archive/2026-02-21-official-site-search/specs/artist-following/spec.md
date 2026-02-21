## MODIFIED Requirements

### Requirement: Persist User Follow Actions

The system SHALL persist user follow and unfollow actions for specific artists in a relational database. After a follow is successfully persisted, the system SHALL asynchronously attempt to resolve and store the artist's official site URL if one does not already exist.

#### Scenario: Successfully following an artist

- **WHEN** a user with a valid ID requests to follow an artist with a valid MBID
- **THEN** the system SHALL create a record in the `followed_artists` table linking the user to the artist
- **AND** the system SHALL trigger an asynchronous resolution of the artist's official site URL
- **AND** the RPC response SHALL be returned before the resolution completes

#### Scenario: Following an artist whose official site is already known

- **WHEN** a user follows an artist that already has an `artist_official_site` record
- **THEN** the system SHALL create the `followed_artists` record as normal
- **AND** SHALL skip official site resolution silently
