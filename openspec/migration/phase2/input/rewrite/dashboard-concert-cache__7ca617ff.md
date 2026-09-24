<!-- spec: dashboard-concert-cache | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: listFollowed RPC provides hype data on every dashboard load -->

### Requirement: listFollowed RPC provides hype data on every dashboard load
`FollowServiceClient.getFollowedArtistMap()` SHALL call `listFollowed()` on every invocation to retrieve per-artist hype levels, which are not stored in the in-memory `followedArtists: Artist[]` array.

> **Note**: Skipping `listFollowed()` when `followedArtists` is already populated was considered but deferred. `followedArtists` stores only `Artist[]` (no hype), so skipping the RPC would drop hype data from dashboard rendering. This optimization is a future opportunity once `followedArtists` is refactored to `FollowedArtist[]`.

#### Scenario: Follow state already in memory
- **WHEN** `getFollowedArtistMap()` is called and `followedArtists.length > 0`
- **THEN** `listFollowed()` SHALL still be called to retrieve current hype levels

#### Scenario: Follow state not yet loaded
- **WHEN** `getFollowedArtistMap()` is called and `followedArtists` is empty
- **THEN** `listFollowed()` SHALL be called to populate the state and retrieve hype levels
