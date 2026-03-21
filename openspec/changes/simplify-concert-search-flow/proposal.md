## Why

The discovery page's concert search polling has a bug: the Coach Mark display condition requires **all** followed artists' searches to complete (`completedSearchCount >= followedCount`), but `followedCount` grows dynamically as the user keeps following. This creates a moving goalpost where the Coach Mark may never appear if the user follows artists faster than searches complete. The root cause is over-engineered orchestration — `FollowOrchestrator` and `ConcertSearchTracker` duplicate state and logic that should live in singleton services.

## What Changes

- **Fix Coach Mark condition**: Change from "all searches complete + any concert exists" to "3+ artists with concerts found" — matching the intended UX.
- **Remove `FollowOrchestrator`**: Push follow state (`followedArtists`, `followedIds`, `followedCount`) into `FollowServiceClient` as `@observable` SSoT, consistent with the `GuestService` state management pattern.
- **Remove `ConcertSearchTracker`**: Move polling logic (`searchNewConcerts` → `listSearchStatuses` → `listConcerts`) into `ConcertServiceClient`. The service tracks `artistsWithConcerts` as `@observable` state, reusable by Dashboard.
- **Remove `verifyConcertsExist`**: Replace batch-verify-after-all-complete with per-artist `listConcerts` check on each search completion. Eliminates the redundant second round of API calls.
- **Remove `checkLiveEvents`**: The snack notification ("this artist has upcoming events") is produced as a side effect of the per-artist completion check, eliminating the duplicate `listConcerts` call.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `frontend-onboarding-flow`: Coach Mark condition changes from "all searches complete + concert exists" to "3+ artists with concerts found". Pre-seeded follow sync moves to service layer.
- `state-management`: `FollowServiceClient` gains `@observable followedArtists` as SSoT. `ConcertServiceClient` gains `@observable artistsWithConcerts` state and `searchAndTrack()` polling method.

## Impact

- **Frontend only** — no backend or protobuf changes required.
- **Files removed**: `follow-orchestrator.ts`, `concert-search-tracker.ts`
- **Files modified**: `discovery-route.ts` (simplified), `follow-service-client.ts` (SSoT), `concert-service.ts` (polling + state)
- **Files modified (minor)**: `bubble-manager.ts`, `genre-filter-controller.ts` (update references to follow state source)
- **Dashboard**: Can leverage `concertService.artistsWithConcerts` for optimized loading indicators (optional, not required).
