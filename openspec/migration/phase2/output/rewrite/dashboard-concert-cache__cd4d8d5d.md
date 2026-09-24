<!-- spec: dashboard-concert-cache | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: Concert cache is invalidated on follow -->

### Requirement: Concert cache is invalidated on follow
`ConcertServiceClient` SHALL invalidate the follower-scoped concert cache, and `FollowServiceClient`'s `follow()`, `unfollow()`, and `setHype()` methods SHALL trigger that invalidation after the RPC succeeds, so the next dashboard load fetches fresh concert data. The invalidation SHALL NOT occur when the mutation RPC fails.

#### Scenario: Cache invalidated after follow
- **WHEN** the user successfully follows or unfollows an artist, or changes an artist's hype
- **THEN** the `listByFollower()` cache SHALL be invalidated
- **AND** the next call to `listByFollower()` SHALL issue an RPC

#### Scenario: Cache not invalidated on follow RPC failure
- **WHEN** the `follow()`/`unfollow()`/`setHype()` RPC call fails with an error
- **THEN** the `listByFollower()` cache SHALL remain valid
