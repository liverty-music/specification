# dashboard-concert-cache

## Purpose

Defines in-memory caching behavior for concert and follow data on the Dashboard, reducing unnecessary RPC calls while ensuring data freshness after follow actions.

## Requirements

### Requirement: listByFollower results are cached in memory for the session
`ConcertServiceClient` SHALL cache the result of `listByFollower()` in memory within the Aurelia singleton service. The cache SHALL have a TTL of 24 hours. While the cache is valid, subsequent calls to `listByFollower()` SHALL return the cached value without issuing an RPC.

#### Scenario: Cache hit on Dashboard re-entry
- **WHEN** the user navigates to Dashboard a second time within 24 hours without having followed any artists
- **THEN** `listByFollower()` SHALL return the cached result without making an RPC call

#### Scenario: Cache miss on first load
- **WHEN** `listByFollower()` is called and no cached value exists
- **THEN** the RPC SHALL be issued and the result SHALL be stored in the cache with the current timestamp

#### Scenario: Cache expiry after 24 hours
- **WHEN** `listByFollower()` is called more than 24 hours after the cache was last populated
- **THEN** the RPC SHALL be issued and the cache SHALL be refreshed

### Requirement: Concert cache is invalidated on follow
`ConcertServiceClient` SHALL expose an `invalidateFollowerCache()` method. `FollowServiceClient.follow()` SHALL call `invalidateFollowerCache()` after the follow RPC succeeds, so the next dashboard load fetches fresh concert data.

#### Scenario: Cache invalidated after follow
- **WHEN** the user successfully follows an artist
- **THEN** the `listByFollower()` cache SHALL be invalidated
- **AND** the next call to `listByFollower()` SHALL issue an RPC

#### Scenario: Cache not invalidated on follow RPC failure
- **WHEN** the `follow()` RPC call fails with an error
- **THEN** the `listByFollower()` cache SHALL remain valid

### Requirement: listFollowed RPC provides hype data on every dashboard load
`FollowServiceClient.getFollowedArtistMap()` SHALL call `listFollowed()` on every invocation to retrieve per-artist hype levels, which are not stored in the in-memory `followedArtists: Artist[]` array.

> **Note**: Skipping `listFollowed()` when `followedArtists` is already populated was considered but deferred. `followedArtists` stores only `Artist[]` (no hype), so skipping the RPC would drop hype data from dashboard rendering. This optimization is a future opportunity once `followedArtists` is refactored to `FollowedArtist[]`.

#### Scenario: Follow state already in memory
- **WHEN** `getFollowedArtistMap()` is called and `followedArtists.length > 0`
- **THEN** `listFollowed()` SHALL still be called to retrieve current hype levels

#### Scenario: Follow state not yet loaded
- **WHEN** `getFollowedArtistMap()` is called and `followedArtists` is empty
- **THEN** `listFollowed()` SHALL be called to populate the state and retrieve hype levels
