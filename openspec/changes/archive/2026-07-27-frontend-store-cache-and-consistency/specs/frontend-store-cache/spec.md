## ADDED Requirements

### Requirement: Shared stale-while-revalidate cache primitive
The frontend SHALL provide a single shared revalidating-cache primitive that Aurelia singleton stores use to cache read-only RPC resources. The primitive SHALL, for a given cache key, return any cached value immediately (stale-while-revalidate) and issue the underlying fetcher only when no value exists or the cached value is older than the resource's configured `staleTime`. The primitive SHALL be an internal collaborator of a store: the store's observable state SHALL remain the single public read surface, and no component SHALL read the cache directly.

#### Scenario: Cached value served immediately while fresh
- **WHEN** a store requests a resource whose cached value is within its `staleTime`
- **THEN** the primitive SHALL return the cached value
- **AND** it SHALL NOT issue the fetcher

#### Scenario: Stale value served then revalidated
- **WHEN** a store requests a resource whose cached value is older than its `staleTime`
- **THEN** the primitive SHALL return the cached value immediately
- **AND** it SHALL issue the fetcher in the background and replace the cached value when it resolves

#### Scenario: Miss issues the fetcher
- **WHEN** a store requests a resource for which no cached value exists
- **THEN** the primitive SHALL issue the fetcher and store the result with the current timestamp under its cache key

#### Scenario: Single copy, no parallel state
- **WHEN** a resource is cached via the primitive
- **THEN** exactly one copy of that resource SHALL exist, owned by its store
- **AND** components SHALL read that resource only through the store's observable state, never from the cache directly

### Requirement: In-flight request coalescing
The primitive SHALL coalesce concurrent requests for the same cache key into a single in-flight fetch, so that simultaneous callers share one RPC and one result.

#### Scenario: Concurrent callers share one fetch
- **WHEN** two callers request the same cache key while a fetch for that key is already in flight
- **THEN** both callers SHALL receive the result of the single in-flight fetch
- **AND** no second RPC SHALL be issued for that key

### Requirement: Complete cache keys
Each cached resource SHALL be keyed by every input that changes its result. `Artist.listTop` SHALL be keyed by `country + tag + limit`. `Concert.listWithProximity` SHALL be keyed by the sorted artist-id set plus country code and level-1 area. A cache lookup SHALL NOT return a value produced for a different set of inputs.

#### Scenario: listTop key includes limit
- **WHEN** `listTop` is requested with the same country and tag but a different `limit`
- **THEN** the primitive SHALL treat it as a distinct key
- **AND** it SHALL NOT return a value cached for the other `limit`

#### Scenario: Proximity key includes the artist set and area
- **WHEN** `listWithProximity` is requested with a different artist-id set or a different country/level-1 area
- **THEN** the primitive SHALL treat it as a distinct key

### Requirement: Explicit invalidation on mutations
The primitive SHALL expose explicit invalidation so that a mutation can force the next read of an affected resource to refetch. Each cached resource SHALL have its invalidating writes defined so no write leaves a stale cache:
- A successful `follow`/`unfollow` SHALL invalidate the follower-scoped concert cache (`listByFollower`).
- A successful `setHype` SHALL invalidate the follower-scoped concert cache (`listByFollower`), because hype is rendered from that data.
- A successful ticket mint (a new ticket becoming available to the user) SHALL invalidate `listTickets`.
- `listWithProximity` requires no write-side invalidation: it is keyed by the guest artist-id set, so changing the follow set produces a new key rather than a stale one.
- `listTop` requires no write-side invalidation: it has no user-write inputs and relies on `staleTime`/resume revalidation for freshness.

#### Scenario: Invalidated key refetches
- **WHEN** a cache key is invalidated
- **THEN** the next request for that key SHALL issue the fetcher rather than return a cached value

#### Scenario: Follow or hype change invalidates follower concerts
- **WHEN** the user successfully follows, unfollows, or changes the hype of an artist
- **THEN** the follower-scoped concert cache (`listByFollower`) SHALL be invalidated
- **AND** the next request for it SHALL refetch

#### Scenario: New ticket invalidates the ticket list
- **WHEN** a new ticket becomes available to the user (mint)
- **THEN** the `listTickets` cache SHALL be invalidated
- **AND** the next request for it SHALL refetch

#### Scenario: Proximity cache needs no write-side invalidation
- **WHEN** the guest follow set changes
- **THEN** `listWithProximity` SHALL be requested under a new key derived from the new artist-id set
- **AND** no explicit invalidation of the prior key SHALL be required for correctness

### Requirement: Revalidation on route entry and PWA resume
Stores that cache resources SHALL revalidate them in the background on route entry and when the installed PWA returns to the foreground. "Foreground view" SHALL mean the resources owned by the stores backing the currently active route (the route whose component is attached in the viewport at resume time); revalidation SHALL NOT fan out to stores whose route is not currently active. Foreground return SHALL be detected via the Page Visibility signal (`visibilitychange` to `visible` / resume). Revalidation SHALL be non-destructive: the cached value SHALL continue to render and SHALL be replaced in place when fresh data arrives, without a full document reload.

#### Scenario: Route entry paints cache then revalidates
- **WHEN** the user navigates to a page backed by a cached resource
- **THEN** the store SHALL render the cached value immediately
- **AND** it SHALL revalidate the resource in the background

#### Scenario: PWA resume revalidates stale data
- **WHEN** the installed PWA returns to the foreground after being backgrounded
- **THEN** stale cached resources owned by the stores backing the currently active route SHALL be revalidated in the background
- **AND** cached resources for routes that are not currently active SHALL NOT be revalidated by the resume signal

#### Scenario: Revalidation does not reload or jump
- **WHEN** a background revalidation replaces a cached value
- **THEN** the update SHALL occur in place via the store's observable state
- **AND** it SHALL NOT trigger a full document reload or reset scroll position

### Requirement: Caching scope is limited to audited read resources
The primitive SHALL be applied only to read-only resources whose value derives from cross-route re-entry: `Concert.listByFollower`, `Concert.listWithProximity`, `Artist.listTop`, and `Ticket.listTickets`. Resources that are requested at most once per session, are network-first for freshness, or are client-owned local state SHALL NOT be cached by the primitive. `User.get` SHALL remain out of scope: it keeps its existing idempotent get-or-create recovery (in-memory + localStorage) and SHALL NOT be migrated onto the primitive.

#### Scenario: One-shot per-artist reads are not cached
- **WHEN** `Concert.listConcerts(artistId)` or `Artist.listSimilar(artistId)` is requested
- **THEN** it SHALL be issued as a direct pass-through
- **AND** it SHALL NOT be stored in the primitive

#### Scenario: Network-first resources are not cached
- **WHEN** a network-first resource (`Entry.getMerklePath`, `Push.*`, `Artist.search`) is requested
- **THEN** it SHALL be issued fresh
- **AND** it SHALL NOT be served from the primitive

#### Scenario: User.get is not migrated onto the primitive
- **WHEN** the current user entity is read via `User.get`
- **THEN** it SHALL be served by its existing idempotent get-or-create recovery (in-memory + localStorage)
- **AND** it SHALL NOT be routed through the shared primitive
