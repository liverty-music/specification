## Why

The dashboard loads concerts by making one `ConcertService.List` RPC call per followed artist (N+1 problem). A user following 50 artists triggers 50 RPC round-trips and 50 SQL queries. This does not scale and wastes server resources. The fix is to add a single RPC that returns all concerts for the authenticated user's followed artists in one call.

## What Changes

- Add `ListByFollower` RPC to `ConcertService` that returns all concerts for the caller's followed artists in a single request
- Add backend handler, usecase, and repository methods to support the new RPC with a single SQL query joining `concerts`, `events`, `venues`, and `followed_artists`
- Replace the frontend dashboard's N parallel `ListConcerts` calls with one `ListByFollower` call

## Capabilities

### New Capabilities

_(none — this extends existing capabilities)_

### Modified Capabilities

- `concert-service`: Add `ListByFollower` RPC that retrieves concerts for all artists followed by the authenticated user
- `live-events`: Add scenario for listing concerts by follower

## Impact

- **Proto**: `concert_service.proto` — new RPC, request, and response messages
- **Backend**: `concert_handler.go`, `concert_uc.go`, `concert_repo.go` — new methods
- **Frontend**: `dashboard-service.ts`, `concert-service.ts` — replace N calls with 1
- **No breaking changes**: Existing `List` RPC is unchanged
