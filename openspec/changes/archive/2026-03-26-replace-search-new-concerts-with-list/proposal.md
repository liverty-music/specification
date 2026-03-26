## Why

The Discovery page currently calls `SearchNewConcerts` directly from the frontend after a user follows an artist. This is wrong: `SearchNewConcerts` is an expensive AI-powered external search (up to 60 seconds, Gemini + Google Search) and should only be triggered by the cronjob or the backend's first-follow logic — not by the UI on every follow action. The Discovery page only needs to display already-stored upcoming concerts for followed artists.

## What Changes

- **REMOVE** `searchNewConcerts` calls from the frontend Discovery page route (`discovery-route.ts`)
- **REPLACE** with a direct call to the existing `List` RPC (per-artist, returns stored concerts)
- **REMOVE** `searchNewConcerts` method from `ConcertServiceClient` (no longer called from frontend)
- The backend's `triggerFirstFollowSearch` (follow usecase) continues to trigger `SearchNewConcerts` for genuinely new artists — no backend changes required

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `follow-triggered-search`: The frontend SHALL NOT independently call `SearchNewConcerts` after a follow. Concert discovery is solely the responsibility of the backend (first-follow trigger) and the cronjob.
- `discover`: After following an artist on the Discovery page, the page SHALL call `ConcertService.List` to check for existing concerts and update onboarding state, instead of calling `SearchNewConcerts`.

## Impact

- **Frontend** (`discovery-route.ts`, `concert-service.ts`): Remove `searchNewConcerts` calls and the method itself
- **No proto changes**: `SearchNewConcerts` RPC remains in the schema (still used by backend and cronjob)
- **No backend changes**: `follow_uc.go` `triggerFirstFollowSearch` is unchanged
- **UX**: Snack notification ("X has upcoming events") and onboarding coach mark still fire — but only if concerts already exist in DB at the time of follow. New concerts discovered asynchronously by the backend will not immediately surface in a snack (acceptable trade-off for this change; polling is out of scope).
