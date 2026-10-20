## MODIFIED Requirements

### Requirement: ListFollowed results are cached in memory for the session
The app SHALL cache the result of `ConcertService.ListFollowed` in memory for the duration of the session, using the shared caching mechanism used by other stores rather than bespoke per-store logic. The cache SHALL use a `staleTime` of 24 hours. While the cached value is within `staleTime`, the dashboard SHALL be served the cached value without issuing an RPC, including when the fan navigates back to Dashboard from another screen. The cached value SHALL be refreshed only by these triggers: the cached value passing `staleTime`, the installed PWA returning to the foreground, and the invalidation on follow described in "Concert cache is invalidated on follow". Because the cache lives in memory, restarting the app SHALL discard it, so the first Dashboard load after a restart calls `ConcertService.ListFollowed`.

#### Scenario: Cache hit on Dashboard re-entry
- **WHEN** the user navigates to Dashboard a second time within 24 hours without having followed or unfollowed any artists
- **THEN** the cached `ConcertService.ListFollowed` result SHALL be returned immediately without blocking on an RPC
- **AND** `ConcertService.ListFollowed` SHALL NOT be called

#### Scenario: Cache miss on first load
- **WHEN** the dashboard needs the followed artists' concerts and no cached value exists
- **THEN** `ConcertService.ListFollowed` SHALL be called and the result SHALL be stored in the cache with the current timestamp

#### Scenario: Cache expiry after 24 hours
- **WHEN** the dashboard needs the followed artists' concerts more than 24 hours after the cache was last populated
- **THEN** the cached value SHALL be served immediately and `ConcertService.ListFollowed` SHALL be called in the background to refresh the cache

#### Scenario: Revalidation on PWA resume
- **WHEN** the installed PWA returns to the foreground on the Dashboard after being backgrounded
- **THEN** the app SHALL revalidate the `ConcertService.ListFollowed` result in the background, even when the cached value is within 24 hours
- **AND** the refreshed value SHALL replace the cached value in place without a full document reload
