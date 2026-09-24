<!-- spec: dashboard-concert-cache | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: listFollowed RPC provides hype data on every dashboard load -->

### Requirement: listFollowed RPC provides hype data on every dashboard load
`FollowServiceClient.getFollowedArtistMap()` SHALL call `listFollowed()` on every invocation to retrieve per-artist hype levels, which are not stored in the in-memory list of followed artists.

#### Scenario: Follow state already in memory
- **WHEN** `getFollowedArtistMap()` is called and the in-memory list of followed artists already has entries
- **THEN** `listFollowed()` SHALL still be called to retrieve current hype levels

#### Scenario: Follow state not yet loaded
- **WHEN** `getFollowedArtistMap()` is called and the in-memory list of followed artists is empty
- **THEN** `listFollowed()` SHALL be called to populate the state and retrieve hype levels
