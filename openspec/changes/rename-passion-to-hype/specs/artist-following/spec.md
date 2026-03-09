## MODIFIED Requirements

### Requirement: Follow Relationship Data Model

The system SHALL maintain a follow relationship between users and artists, stored in the followed_artists table. The use case layer SHALL resolve the authenticated user's external identity (Zitadel `sub` claim) to the internal user UUID before querying or writing to the `followed_artists` table.

#### Scenario: Hype stored on follow relationship

- **GIVEN** the followed_artists table
- **WHEN** a follow relationship exists
- **THEN** a `hype` column SHALL store the user's enthusiasm tier (watch, home, nearby, anywhere) with a default of `anywhere`

#### Scenario: Successfully following an artist

- **WHEN** a user with a valid Zitadel identity requests to follow an artist with a valid MBID
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID via `UserRepository.GetByExternalID`
- **AND** the system SHALL create a record in the `followed_artists` table linking the internal user UUID to the artist
- **AND** the `hype` column SHALL default to `anywhere`

#### Scenario: User record not found during follow

- **WHEN** `Follow` is called with a valid Zitadel identity but no corresponding user record exists
- **THEN** the system SHALL return `NOT_FOUND` error indicating the user must complete registration first

### Requirement: ListFollowed Response

The system SHALL return the user's followed artists via the ListFollowed RPC.

#### Scenario: Response uses FollowedArtist wrapper with hype

- **GIVEN** a user calls ListFollowed
- **WHEN** the response is returned
- **THEN** each entry SHALL be a FollowedArtist wrapper containing the artist entity and the user's hype level (HypeType enum)
