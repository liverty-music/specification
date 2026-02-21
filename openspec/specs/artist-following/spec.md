## Purpose

This capability enables users to follow and unfollow musical artists, creating a personalized foundation for event discovery and notifications.

## Requirements

### Requirement: Persist User Follow Actions
The system SHALL persist user follow and unfollow actions for specific artists in a relational database. The frontend SHALL call the backend `ArtistService.Follow` RPC when a user taps an artist bubble. After a follow is successfully persisted, the system SHALL asynchronously attempt to resolve and store the artist's official site URL if one does not already exist.

#### Scenario: Successfully following an artist
- **WHEN** a user with a valid ID requests to follow an artist with a valid MBID
- **THEN** the system SHALL create a record in the `followed_artists` table linking the user to the artist
- **AND** the system SHALL trigger an asynchronous resolution of the artist's official site URL
- **AND** the RPC response SHALL be returned before the resolution completes

#### Scenario: Following an artist whose official site is already known

- **WHEN** a user follows an artist that already has an `artist_official_site` record
- **THEN** the system SHALL create the `followed_artists` record as normal
- **AND** SHALL skip official site resolution silently

#### Scenario: Frontend calls Follow RPC on bubble tap
- **WHEN** a user taps an artist bubble in the discovery UI
- **THEN** the frontend SHALL call `ArtistService.Follow` RPC with the artist's database-assigned `id`
- **AND** the frontend SHALL update local state immediately without waiting for the RPC response
- **AND** any RPC error SHALL be logged but SHALL NOT block the UI interaction

### Requirement: Idempotent Unfollow Logic
The system SHALL allow users to unfollow artists, ensuring that the operation is idempotent.

#### Scenario: Unfollowing an artist
- **WHEN** a user requests to unfollow an artist they currently follow
- **THEN** the system SHALL remove the corresponding record from the `followed_artists` table

### Requirement: Follow Status Verification
The system SHALL provide a way to verify if a specific user follows a specific artist.

#### Scenario: Checking follow status
- **WHEN** querying the follow status for a user-artist pair
- **THEN** the system SHALL return a boolean indicating whether the follow record exists

### Requirement: List All Followed Artists

The `ArtistRepository` SHALL provide a `ListAllFollowed` method that returns all distinct artists followed by any user in the system.

#### Scenario: Multiple users follow the same artist

- **WHEN** `ListAllFollowed` is called and multiple users follow the same artist
- **THEN** the artist SHALL appear only once in the result set

#### Scenario: No followed artists

- **WHEN** `ListAllFollowed` is called and no users follow any artists
- **THEN** it SHALL return an empty slice without error

#### Scenario: Mixed followed and unfollowed artists

- **WHEN** some artists in the system have followers and others do not
- **THEN** only artists with at least one follower SHALL be returned
