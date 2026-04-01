## Why

The artist filter bar bottom sheet always displays an empty list of followed artists, making the feature non-functional for users who want to filter concerts by their followed artists. The bug exists because `FollowServiceClient.listFollowed()` fetches from RPC/guest but never writes back to the `followedArtists` observable property, so the UI binding always sees `[]`.

## What Changes

- `FollowServiceClient.listFollowed()` will update `this.followedArtists` after fetching, ensuring the observable stays in sync with the latest server/guest state.
- New unit tests will be added for `ArtistFilterBar` to cover the empty-sheet, multi-artist name resolution, double-open reset, and invalid-dismiss scenarios.
- Integration test coverage for the `listFollowed()` side-effect will be noted/added in `FollowServiceClient` spec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `artist-following`: The `listFollowed()` method now has a side-effect of updating the cached `followedArtists` observable, so that components reading `followedArtists` after a `listFollowed()` call see the correct list.

## Impact

- **Frontend only** — single source file change: `frontend/src/services/follow-service-client.ts`
- No API, proto, or backend changes required.
- Components reading `followedArtists` (e.g., `DashboardRoute`, `ArtistFilterBar`) will automatically receive the correct list after `listFollowed()` completes.
- Existing `follow()` and `unfollow()` optimistic-update paths are unchanged.
