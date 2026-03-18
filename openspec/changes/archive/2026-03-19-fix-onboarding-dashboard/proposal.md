## Why

Onboarding dashboard is broken: coach mark spotlights fail to appear on stage headers, and all concerts are placed in the AWAY lane regardless of user's home selection. This blocks the lane introduction sequence, preventing users from completing the onboarding tutorial (discovery → dashboard → my-artists).

Root causes:
1. CSS attribute selectors use `[data-stage-home]` but HTML uses `data-stage="home"` — coach mark targets are never found.
2. Frontend `groupConcertsByDate()` places all concerts in `away` because no server-side proximity classification exists for unauthenticated onboarding users.
3. Coach mark retry timers are not cancelled when a new phase starts, causing leaked timers.

## What Changes

- **New RPC `ListWithProximity`** on `ConcertService`: accepts `repeated ArtistId` + `Home`, returns `repeated ProximityGroup`. Public (no auth required). Shares `GroupByDateAndProximity` logic with existing `ListByFollower`.
- **Fix coach mark CSS selectors**: change `[data-stage-home]` → `[data-stage="home"]` (and near, away) in `dashboard-route.ts`.
- **Fix retry timer leak**: cancel pending retry timer in `findAndHighlight()` before starting a new retry chain.
- **Replace N client-side `List` calls** with single `ListWithProximity` call during onboarding.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `concert-service`: Add `ListWithProximity` RPC — accepts `repeated ArtistId` + `Home`, returns `repeated ProximityGroup` for unauthenticated users.
- `dashboard-lane-introduction`: Fix CSS attribute selector mismatch for stage header spotlights.
- `onboarding-spotlight`: Fix retry timer leak when `findAndHighlight()` is re-invoked before previous retry chain completes.

## Impact

- **specification**: New `ListWithProximity` RPC + request/response messages in `concert_service.proto`.
- **backend**: New handler, use case method, repository method (`ListByArtists` for multiple artist IDs with coordinates).
- **frontend**: Replace `listByFollowerOnboarding()` N-call pattern with single `ListWithProximity` RPC call. Fix selectors and timer leak in dashboard-route and coach-mark components.
- **No breaking changes**: existing `List` and `ListByFollower` RPCs are unchanged.
