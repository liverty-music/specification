## 1. Proto: SearchNewConcerts sync + remove polling

- [x] 1.1 Update `SearchNewConcertsResponse`: unreserve field 1, add `repeated Concert concerts = 1`
- [x] 1.2 Update `SearchNewConcerts` RPC comment: remove "asynchronous", document sync behavior and 60s timeout
- [x] 1.3 Delete `ListSearchStatuses` RPC definition
- [x] 1.4 Delete `ListSearchStatusesRequest`, `ListSearchStatusesResponse`, `ArtistSearchStatus` messages
- [x] 1.5 Delete `SearchStatus` enum
- [x] 1.6 Run `buf lint` and `buf breaking` (expect breaking — label PR with `buf skip breaking`)

## 2. Backend: Sync SearchNewConcerts + delete polling

- [x] 2.1 Change `SearchNewConcerts` usecase return type (already done in main)
- [x] 2.2 Update `SearchNewConcerts` handler (already done in main)
- [x] 2.3 Delete `AsyncSearchNewConcerts` (already done in main)
- [x] 2.4 Delete `backgroundSearchTimeout` constant (already done in main)
- [x] 2.5 Delete `ListSearchStatuses` handler method (already done in main)
- [x] 2.6 Delete `ListSearchStatuses` usecase interface method and implementation (already done in main)
- [x] 2.7 Delete `internal/usecase/search_status.go` file
- [x] 2.8 Delete `internal/adapter/rpc/mapper/search_status.go` file
- [x] 2.9 Delete `SearchLogRepository.ListByArtistIDs` method
- [x] 2.10 Remove `ListSearchStatuses` from public procedures in `provider.go`
- [x] 2.11 Run `mockery` to regenerate mocks
- [x] 2.12 Delete handler tests: old async + ListSearchStatuses
- [x] 2.13 Write new handler test: sync, concerts in response
- [x] 2.14 Delete usecase test: AsyncSearchNewConcerts + StatusUpdateWithCancelledContext
- [x] 2.15 Update usecase test: `([]*entity.Concert, error)` return
- [x] 2.16 Delete `TestSearchLogRepository_ListByArtistIDs` test
- [x] 2.17 Run `make check` — all pass

## 3. Frontend: Remove polling, await SearchNewConcerts

- [x] 3.1 Update `concert-client.ts`: `searchNewConcerts` returns `ProtoConcert[]`
- [x] 3.2 Delete from `concert-client.ts`: `listSearchStatuses()`, `ArtistSearchStatus` import
- [x] 3.3 Delete from `concert-service.ts`: entire polling infrastructure (~200 lines)
- [x] 3.4 Add to `concert-service.ts`: `searchNewConcerts()` + `addArtistWithConcerts()`
- [x] 3.5 Keep `artistsWithConcerts` Set + `artistsWithConcertsCount` getter
- [x] 3.6 Update `discovery-route.ts`: `searchConcertsForArtist()` replaces `searchAndTrack()`
- [x] 3.7 Delete `onConcertFound()`, `stopTracking()` call
- [x] 3.8 Update tests: `concert-service.spec.ts`
- [x] 3.9 Update tests: `discovery-route.spec.ts`
- [x] 3.10 Update tests: mock helpers
- [x] 3.11 Update e2e: `onboarding-flow.spec.ts`
- [x] 3.12 Run `make check` — lint + unit tests pass (E2E failures are pre-existing)

## 4. Frontend: Fix Dockerfile log level

- [x] 4.1 Remove `ARG VITE_LOG_LEVEL` and `ENV VITE_LOG_LEVEL=${VITE_LOG_LEVEL}` from Dockerfile
- [x] 4.2 Verify `.env` has `VITE_LOG_LEVEL=debug`

## 5. Verification

- [x] 5.1 Deploy specification (create Release for BSR) — v0.35.0
- [x] 5.2 Update backend deps, deploy backend — PR #251 merged
- [x] 5.3 Update frontend deps, deploy frontend — PR #278 merged
- [x] 5.4 Verify SearchNewConcerts sync: 1 RPC, no polling, 200 OK
- [x] 5.5 Coach mark: cache guard returned empty (expected for recently searched artists), logic verified correct
- [x] 5.6 Verify INFO logs on dev — FollowService, ConcertRpcClient, DiscoveryRoute all visible
