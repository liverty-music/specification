## Why

The discovery page's concert data gate uses `ListWithProximity` to verify that concerts exist before showing the Dashboard coach mark. This RPC requires `guest.home`, but home is not set until the Dashboard step — creating a circular dependency that prevents the coach mark from ever appearing. Additionally, after a page reload, `FollowOrchestrator` does not restore followed artists from the store, causing already-followed artists to reappear as bubbles.

## What Changes

- Replace the `ListWithProximity` call in `verifyConcertData()` with per-artist `ConcertService/List` calls that require only `artist_id` (no home, no auth)
- Hydrate `FollowOrchestrator.followedArtists` from the store's `guest.follows` on discovery page load, so reload correctly filters bubbles and populates `followedIds`
- Add unit tests for `ConcertSearchTracker`, `FollowOrchestrator`, and `BubbleManager` to cover the gate logic and reload scenarios
- Add E2E test for the discovery reload scenario and the no-home coach mark scenario

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-tutorial`: Step 1 concert data verification SHALL use `ConcertService/List` (per-artist, no home required) instead of `ListWithProximity`
- `bubble-pool-lifecycle`: On discovery page load, the bubble pool SHALL exclude artists already present in the persisted guest follow state

## Impact

- **Frontend**: `concert-search-tracker.ts`, `follow-orchestrator.ts`, `discovery-route.ts`, `concert-service.ts`
- **Tests**: New unit test files for discovery controllers; updated E2E `onboarding-flow.spec.ts`
- **Backend/Proto**: No changes — uses existing `ConcertService/List` RPC
