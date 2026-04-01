## MODIFIED Requirements

### Requirement: ListFollowed Response

The system SHALL return the user's followed artists via the ListFollowed RPC. After the response is received, the client-side `FollowServiceClient.followedArtists` observable SHALL be updated to reflect the fetched list, so that UI components bound to `followedArtists` display the correct set of artists without requiring a separate trigger.

#### Scenario: Response uses FollowedArtist wrapper

- **WHEN** a user calls ListFollowed
- **THEN** each entry SHALL be a FollowedArtist wrapper containing the artist entity and the user's passion level

#### Scenario: followedArtists observable updated after fetch (authenticated)

- **WHEN** `listFollowed()` is called for an authenticated user and the RPC returns a non-empty list
- **THEN** `FollowServiceClient.followedArtists` SHALL be set to the array of Artist objects extracted from the response

#### Scenario: followedArtists observable updated after fetch (guest)

- **WHEN** `listFollowed()` is called for a guest user and guest storage contains followed artists
- **THEN** `FollowServiceClient.followedArtists` SHALL be set to the array of Artist objects extracted from guest follows

#### Scenario: followedArtists observable set to empty when no follows exist

- **WHEN** `listFollowed()` is called and the result is an empty list
- **THEN** `FollowServiceClient.followedArtists` SHALL be set to `[]`

## ADDED Requirements

### Requirement: ArtistFilterBar sheet initializes pendingIds from followedArtists

The ArtistFilterBar component SHALL initialize `pendingIds` from the current `followedArtists` list when `openSheet()` is called.

#### Scenario: Empty followedArtists on openSheet

- **WHEN** `followedArtists` is `[]` and `openSheet()` is called
- **THEN** `pendingIds` SHALL be `[]`

#### Scenario: Multiple followed artists on openSheet

- **WHEN** `followedArtists` contains multiple artists and `openSheet()` is called
- **THEN** `artistNameFor()` SHALL resolve the correct name for each artist in `followedArtists`

#### Scenario: openSheet called twice resets pendingIds

- **WHEN** `openSheet()` is called a second time after state was modified
- **THEN** `pendingIds` SHALL be reset to `selectedIds`, discarding any uncommitted changes from the previous session

#### Scenario: dismiss with unknown ID does not modify selectedIds

- **WHEN** `dismiss()` is called with an artist ID that is not in `selectedIds`
- **THEN** `selectedIds` SHALL remain unchanged
