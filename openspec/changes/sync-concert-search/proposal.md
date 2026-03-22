## Why

The onboarding follow flow is broken because the frontend's concert search polling times out (15s) before the backend's Gemini API completes (~8-60s for multiple artists). The async fire-and-forget + polling architecture adds unnecessary complexity — 6+ RPC calls per artist with fragile timeout logic. A synchronous SearchNewConcerts that waits for Gemini and returns concerts directly eliminates polling entirely, making the system simpler and more reliable.

Additionally, the frontend's `VITE_LOG_LEVEL` Dockerfile ARG overrides `.env` with an empty string, keeping the log level at `warn` on the dev environment despite the previous fix.

## What Changes

- **BREAKING**: `SearchNewConcerts` RPC changes from async (fire-and-forget, empty response) to sync (blocks until Gemini completes, returns concerts). Timeout is 60s via context.
- **BREAKING**: Remove `ListSearchStatuses` RPC entirely — no longer needed without polling.
- **BREAKING**: Remove `SearchStatus` enum, `ArtistSearchStatus`, `ListSearchStatusesRequest/Response` messages from proto.
- **Proto**: Unreserve field 1 on `SearchNewConcertsResponse` and add `repeated Concert concerts = 1`.
- **Backend**: Delete `AsyncSearchNewConcerts`, polling infrastructure, `SearchStatusValue` enum, status mapper. Simplify `SearchLogRepository` (remove `ListByArtistIDs`, keep `GetByArtistID` for 24h cache guard).
- **Frontend**: Delete entire polling infrastructure (~250 lines) from `ConcertService`. Replace `searchAndTrack()` with direct `await searchNewConcerts()`. Delete `listSearchStatuses` RPC client method.
- **Frontend**: Remove `ARG/ENV VITE_LOG_LEVEL` from Dockerfile to let `.env` value flow through correctly.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `concert-search`: SearchNewConcerts becomes synchronous, returns concerts, removes ListSearchStatuses
- `follow-triggered-search`: Frontend replaces polling with direct await on SearchNewConcerts
- `frontend-onboarding-flow`: Coach mark logic unchanged but concert discovery trigger simplified
- `frontend-observability`: Fix Dockerfile log level override

## Impact

- **Proto** (`concert_service.proto`): Breaking change — removed RPCs and messages require a new major version or coordinated rollout
- **Backend**: `concert_handler.go`, `concert_uc.go`, `search_status.go` (delete), `mapper/search_status.go` (delete), `provider.go`, tests
- **Frontend**: `concert-service.ts`, `concert-client.ts`, `discovery-route.ts`, `Dockerfile`, tests, e2e mocks
- **CronJob**: No impact — already uses sync `SearchNewConcerts` directly
