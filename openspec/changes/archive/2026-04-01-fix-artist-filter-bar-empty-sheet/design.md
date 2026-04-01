## Context

The artist filter bar bottom sheet (`frontend/src/components/artist-filter-bar/`) renders a list of followed artists so the user can filter concerts. The list is bound to `DashboardRoute.followedArtists`, which delegates to `FollowServiceClient.followedArtists` — an `@observable` array initialized to `[]`.

`FollowServiceClient` has three mutation paths:
1. `follow()` — adds an artist optimistically to `followedArtists`
2. `unfollow()` — removes an artist optimistically from `followedArtists`
3. `listFollowed()` — fetches the full list from RPC (authenticated) or guest storage, but **never assigns the result back to `followedArtists`**

Because `listFollowed()` is called during page load (via `getFollowedArtistMap()`) and it never writes to `followedArtists`, the observable stays empty and the bottom sheet shows nothing.

## Goals / Non-Goals

**Goals:**
- `followedArtists` observable reflects the latest fetched state after any `listFollowed()` call.
- The fix is minimal and contained to a single file.
- New unit tests cover the four identified edge cases in `ArtistFilterBar`.
- Integration coverage for the `listFollowed()` side-effect is tracked or added.

**Non-Goals:**
- Refactoring the broader `FollowServiceClient` caching strategy.
- Adding optimistic rollback or conflict resolution.
- Changing `DashboardRoute`, `ArtistFilterBar` component, or their templates.
- Any backend or proto changes.

## Decisions

### Decision: Update `followedArtists` inside `listFollowed()` (Option A)

After the fetch resolves (both RPC and guest paths), assign:

```typescript
this.followedArtists = result.map((f) => f.artist)
```

**Rationale**: `followedArtists` is intended to be the canonical in-memory cache of followed artist objects. `listFollowed()` is the only method that performs a full refresh, so it is the correct and natural place to sync the cache. This is a one-line addition and does not change the method's return contract.

**Alternatives considered**:
- *Update in `getFollowedArtistMap()`*: `getFollowedArtistMap()` calls `listFollowed()` internally, so updating it there would also work. However, `listFollowed()` is the lower-level contract; updating there ensures any future caller of `listFollowed()` also benefits without extra ceremony.
- *Update in `DashboardRoute` after `getFollowedArtistMap()`*: This would scatter cache management into consumers. Rejected to keep cache ownership in `FollowServiceClient`.

### Decision: Map `FollowedArtist[]` → `Artist[]` for the assignment

`listFollowed()` returns `FollowedArtist[]`. The `followedArtists` property holds `Artist[]`. The mapping `result.map((f) => f.artist)` is already used in the optimistic paths and is correct here.

## Risks / Trade-offs

- **Ordering risk**: If `listFollowed()` is called concurrently, the last settled promise wins. This is acceptable given current single-page sequential load patterns. → Mitigation: no action required for now; document as known limitation.
- **Test coverage gap**: Without new tests, the regression could reappear silently. → Mitigation: add four unit tests to `ArtistFilterBar` spec and track integration coverage in tasks.

## Migration Plan

Single-file change; no migration steps required. The fix takes effect immediately on the next page load that calls `listFollowed()`. No rollback complexity — reverting the one-line addition restores previous behaviour.

## Open Questions

None.
