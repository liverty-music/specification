## Why

During onboarding, the Loading screen (Step 2) skips `SearchNewConcerts` entirely, which is the only mechanism that populates concert data in the database. As a result, the Dashboard (Step 3) always shows an empty state because `ConcertService/List` reads from an empty DB. Additionally, `checkLiveEvents()` in `ArtistDiscoveryService` uses a hash-based mock instead of calling the real `ConcertService/List` RPC, even though the TS Connect client is already available.

## What Changes

- Make `ConcertService/SearchNewConcerts` accessible without authentication by adding it to `publicProcedures` in the backend DI provider.
- Call `SearchNewConcerts` fire-and-forget on each artist follow during the Discover step (Step 1), so concert data is populated in the background while the user continues selecting artists.
- Replace the `checkLiveEvents()` mock implementation with a real `ConcertService/List` RPC call to check whether an artist has upcoming concerts.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `concert-search`: `SearchNewConcerts` RPC gains public (unauthenticated) access. The 24-hour search log cache provides sufficient protection against abuse.
- `frontend-onboarding-flow`: Artist follow during discovery triggers a background `SearchNewConcerts` call in addition to the existing localStorage write.
- `live-events`: `checkLiveEvents()` replaces its mock with a real `ConcertService/List` call.

## Impact

- **Backend**: `backend/internal/di/provider.go` — add one entry to `publicProcedures` map.
- **Frontend**: `frontend/src/services/artist-discovery-service.ts` — add `SearchNewConcerts` fire-and-forget on follow, replace `checkLiveEvents` mock with `ConcertService/List` call.
- **Frontend**: `frontend/src/services/concert-service.ts` — may need a public-facing `searchNewConcerts` call path (no auth header).
- **Security**: `SearchNewConcerts` becomes publicly accessible. Mitigated by existing `searchLog` 24-hour TTL cache that skips Gemini API calls for recently searched artists.
