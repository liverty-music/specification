# Capability: Artist Following

## Purpose

Manage the relationship between users and artists they follow, including follow/unfollow actions and listing followed artists.

## Requirements

### Requirement: Follow Relationship Data Model

The system SHALL maintain a follow relationship between users and artists, stored in the followed_artists table. The use case layer SHALL resolve the authenticated user's external identity (Zitadel `sub` claim) to the internal user UUID before querying or writing to the `followed_artists` table.

#### Scenario: Passion level stored on follow relationship

- **GIVEN** the followed_artists table
- **WHEN** a follow relationship exists
- **THEN** a passion_level column SHALL store the user's enthusiasm tier (must_go, local_only, keep_an_eye) with a default of local_only

#### Scenario: Successfully following an artist
- **WHEN** a user with a valid Zitadel identity requests to follow an artist with a valid MBID
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID via `UserRepository.GetByExternalID`
- **AND** the system SHALL create a record in the `followed_artists` table linking the internal user UUID to the artist

#### Scenario: User record not found during follow

- **WHEN** `Follow` is called with a valid Zitadel identity but no corresponding user record exists
- **THEN** the system SHALL return `NOT_FOUND` error indicating the user must complete registration first

### Requirement: ListFollowed Response

The system SHALL return the user's followed artists via the ListFollowed RPC.

#### Scenario: Response uses FollowedArtist wrapper

- **GIVEN** a user calls ListFollowed
- **WHEN** the response is returned
- **THEN** each entry SHALL be a FollowedArtist wrapper containing the artist entity and the user's passion level

### Requirement: Idempotent Unfollow Logic
The system SHALL allow users to unfollow artists, ensuring that the operation is idempotent. The use case layer SHALL resolve the external identity to the internal user UUID before deleting from `followed_artists`.

#### Scenario: Unfollowing an artist
- **WHEN** a user requests to unfollow an artist they currently follow
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID
- **AND** the system SHALL remove the corresponding record from the `followed_artists` table
