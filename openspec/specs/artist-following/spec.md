# Capability: Artist Following

## Purpose

Manage the relationship between users and artists they follow, including follow/unfollow actions and listing followed artists.

## Requirements

### Requirement: Follow Relationship Data Model

The system SHALL maintain a follow relationship between users and artists, stored in the followed_artists table.

#### Scenario: Passion level stored on follow relationship

- **GIVEN** the followed_artists table
- **WHEN** a follow relationship exists
- **THEN** a passion_level column SHALL store the user's enthusiasm tier (must_go, local_only, keep_an_eye) with a default of local_only

### Requirement: ListFollowed Response

The system SHALL return the user's followed artists via the ListFollowed RPC.

#### Scenario: Response uses FollowedArtist wrapper

- **GIVEN** a user calls ListFollowed
- **WHEN** the response is returned
- **THEN** each entry SHALL be a FollowedArtist wrapper containing the artist entity and the user's passion level
