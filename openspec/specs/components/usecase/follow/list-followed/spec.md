# List Followed

## Purpose

Lists the artists a user follows along with each artist's hype level, for use by clients that need the user's current follow set.

## Requirements

### Requirement: ListFollowed Response

The system SHALL return the user's followed artists via the ListFollowed RPC. The frontend SHALL update the `followedArtists` observable upon receiving the response, and SHALL set it to an empty list when the user has no follows.

#### Scenario: Response uses FollowedArtist wrapper

- **GIVEN** a user calls ListFollowed
- **WHEN** the response is returned
- **THEN** each entry SHALL be a FollowedArtist wrapper containing the artist entity and the user's passion level

#### Scenario: followedArtists observable updated after fetch (authenticated)

- **GIVEN** an authenticated user
- **WHEN** ListFollowed RPC completes successfully
- **THEN** the `followedArtists` observable SHALL be updated with the returned list of followed artists

#### Scenario: followedArtists observable updated after fetch (guest)

- **GIVEN** a guest (unauthenticated) user
- **WHEN** the followed artists fetch is skipped or returns empty
- **THEN** the `followedArtists` observable SHALL be set to an empty list

#### Scenario: followedArtists observable set to empty when no follows exist

- **GIVEN** an authenticated user with no followed artists
- **WHEN** ListFollowed RPC completes and returns an empty list
- **THEN** the `followedArtists` observable SHALL be set to an empty list

### Requirement: HypeLevel in ListFollowed Response

The system SHALL include the user's hype level for each artist in the ListFollowed response, using a FollowedArtist wrapper that contains both the artist entity and the hype level.

#### Scenario: ListFollowed returns hype levels

- **GIVEN** a user follows three artists with different hype levels
- **WHEN** the user calls ListFollowed
- **THEN** each artist in the response SHALL include its corresponding hype level
