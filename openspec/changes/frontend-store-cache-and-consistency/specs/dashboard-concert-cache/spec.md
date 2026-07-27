## MODIFIED Requirements

### Requirement: listByFollower results are cached in memory for the session
`ConcertServiceClient` SHALL cache the result of `listByFollower()` in memory within the Aurelia singleton service, obtaining the caching behavior from the shared `frontend-store-cache` primitive rather than bespoke per-store logic. The cache SHALL use a `staleTime` of 24 hours. While the cached value is within `staleTime`, subsequent calls to `listByFollower()` SHALL return the cached value without issuing an RPC. In addition, the store SHALL revalidate the cached value in the background on Dashboard route entry and when the installed PWA returns to the foreground, so a long-lived session refreshes without a manual reload.

#### Scenario: Cache hit on Dashboard re-entry
- **WHEN** the user navigates to Dashboard a second time within 24 hours without having followed or unfollowed any artists
- **THEN** `listByFollower()` SHALL return the cached result immediately without blocking on an RPC
- **AND** the store SHALL revalidate the value in the background

#### Scenario: Cache miss on first load
- **WHEN** `listByFollower()` is called and no cached value exists
- **THEN** the RPC SHALL be issued and the result SHALL be stored in the cache with the current timestamp

#### Scenario: Cache expiry after 24 hours
- **WHEN** `listByFollower()` is called more than 24 hours after the cache was last populated
- **THEN** the cached value SHALL be served immediately and the RPC SHALL be issued in the background to refresh the cache

#### Scenario: Revalidation on PWA resume
- **WHEN** the installed PWA returns to the foreground on the Dashboard after being backgrounded
- **THEN** the store SHALL revalidate `listByFollower()` in the background
- **AND** the refreshed value SHALL replace the cached value in place without a full document reload

### Requirement: Concert cache is invalidated on follow
`ConcertServiceClient` SHALL invalidate the follower-scoped concert cache through the shared `frontend-store-cache` primitive (rather than a bespoke `invalidateFollowerCache()` field), and `FollowServiceClient.follow()`/`unfollow()`/`setHype()` SHALL trigger that invalidation after the RPC succeeds, so the next dashboard load fetches fresh concert data. The invalidation SHALL NOT occur when the mutation RPC fails.

#### Scenario: Cache invalidated after follow
- **WHEN** the user successfully follows or unfollows an artist, or changes an artist's hype
- **THEN** the `listByFollower()` cache SHALL be invalidated via the primitive
- **AND** the next call to `listByFollower()` SHALL issue an RPC

#### Scenario: Cache not invalidated on follow RPC failure
- **WHEN** the `follow()`/`unfollow()`/`setHype()` RPC call fails with an error
- **THEN** the `listByFollower()` cache SHALL remain valid
