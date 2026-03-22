## 1. Proto: SearchNewConcerts sync + remove polling

- [x] 1.1 Update `SearchNewConcertsResponse`: unreserve field 1, add `repeated Concert concerts = 1`
- [x] 1.2 Update `SearchNewConcerts` RPC comment: remove "asynchronous", document sync behavior and 60s timeout
- [x] 1.3 Delete `ListSearchStatuses` RPC definition
- [x] 1.4 Delete `ListSearchStatusesRequest`, `ListSearchStatusesResponse`, `ArtistSearchStatus` messages
- [x] 1.5 Delete `SearchStatus` enum
- [x] 1.6 Run `buf lint` and `buf breaking` (expect breaking — label PR with `buf skip breaking`)

## 2. Backend: Sync SearchNewConcerts + delete polling

- [ ] 2.1 Change `SearchNewConcerts` usecase return type from `error` to `([]*entity.Concert, error)` — return discovered concerts after persist
- [ ] 2.2 Update `SearchNewConcerts` handler: call sync usecase directly (not `AsyncSearchNewConcerts`), map `[]entity.Concert` to proto, populate response
- [ ] 2.3 Delete `AsyncSearchNewConcerts` interface method and implementation
- [ ] 2.4 Delete `backgroundSearchTimeout` constant
- [ ] 2.5 Delete `ListSearchStatuses` handler method
- [ ] 2.6 Delete `ListSearchStatuses` usecase interface method and implementation
- [ ] 2.7 Delete `internal/usecase/search_status.go` file (SearchStatusValue enum)
- [ ] 2.8 Delete `internal/adapter/rpc/mapper/search_status.go` file
- [ ] 2.9 Delete `SearchLogRepository.ListByArtistIDs` method (entity interface + rdb implementation)
- [ ] 2.10 Remove `ListSearchStatuses` from public procedures in `provider.go`
- [ ] 2.11 Run `mockery` to regenerate mocks
- [ ] 2.12 Delete handler tests: `TestConcertHandler_SearchNewConcerts` (old async), `TestConcertHandler_ListSearchStatuses`
- [ ] 2.13 Write new handler test: `TestConcertHandler_SearchNewConcerts` (sync, concerts in response)
- [ ] 2.14 Delete usecase test: `TestConcertUseCase_AsyncSearchNewConcerts`
- [ ] 2.15 Update usecase test: `TestConcertUseCase_SearchNewConcerts` — expect `([]*entity.Concert, error)` return
- [ ] 2.16 Delete `search_log_repo_test.go` `TestSearchLogRepository_ListByArtistIDs` test
- [ ] 2.17 Run `make check`

## 3. Frontend: Remove polling, await SearchNewConcerts

- [ ] 3.1 Update `concert-client.ts`: `searchNewConcerts` returns `ProtoConcert[]` from response
- [ ] 3.2 Delete from `concert-client.ts`: `listSearchStatuses()` method, `ArtistSearchStatus` import
- [ ] 3.3 Delete from `concert-service.ts`: polling infrastructure (searchAndTrack, pollSearchStatuses, startPollingIfNeeded, stopPolling, markDone, getPendingArtistIds, checkArtistConcerts, onConcertFoundCallback, searchStatus Map, searchStartTimes Map, pollIntervalId, pollAbortSignal, pollTargetCount, POLL_INTERVAL_MS, PER_ARTIST_TIMEOUT_MS, SearchStatusResult, protoStatusToString)
- [ ] 3.4 Add to `concert-service.ts`: simple `searchNewConcerts(artistId, signal)` method that calls RPC and returns concerts
- [ ] 3.5 Keep `concert-service.ts`: `artistsWithConcerts` Set, `artistsWithConcertsCount` getter, `stopTracking()` (rename or remove if unused)
- [ ] 3.6 Update `discovery-route.ts`: replace `searchAndTrack()` calls with `await concertService.searchNewConcerts()` + inline `artistsWithConcerts.add()` + snack notification
- [ ] 3.7 Delete `discovery-route.ts`: `onConcertFound()` method, `concertService.stopTracking()` call in detaching
- [ ] 3.8 Update tests: `concert-service.spec.ts` — delete listSearchStatuses suite, update searchNewConcerts suite
- [ ] 3.9 Update tests: `discovery-route.spec.ts` — replace searchAndTrack expectations with searchNewConcerts await
- [ ] 3.10 Update tests: mock helpers — remove searchAndTrack, stopTracking from mock
- [ ] 3.11 Update e2e: `onboarding-flow.spec.ts` — delete ListSearchStatuses mock, update SearchNewConcerts mock to return concerts
- [ ] 3.12 Run `make check`

## 4. Frontend: Fix Dockerfile log level

- [ ] 4.1 Remove `ARG VITE_LOG_LEVEL` and `ENV VITE_LOG_LEVEL=${VITE_LOG_LEVEL}` from Dockerfile
- [ ] 4.2 Verify `.env` has `VITE_LOG_LEVEL=debug`

## 5. Verification

- [ ] 5.1 Deploy specification (create Release for BSR)
- [ ] 5.2 Update backend deps (`go get buf.build/...`), deploy backend
- [ ] 5.3 Update frontend deps (`npm install`), deploy frontend
- [ ] 5.4 Verify onboarding: follow artist → SearchNewConcerts blocks → concerts returned → snack notification
- [ ] 5.5 Verify coach mark appears after 3 artists with concerts
- [ ] 5.6 Verify browser console shows INFO-level logs on dev.liverty-music.app
