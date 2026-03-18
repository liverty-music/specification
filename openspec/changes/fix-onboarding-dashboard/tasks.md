## 1. Specification (Proto)

- [x] 1.1 Add `ListWithProximityRequest` message to `concert_service.proto` with `repeated ArtistId artist_ids` (max_items=50 via protovalidate) and `entity.v1.Home home` (required)
- [x] 1.2 Add `ListWithProximityResponse` message with `repeated ProximityGroup groups`
- [x] 1.3 Add `rpc ListWithProximity` to `ConcertService`
- [x] 1.4 Run `buf lint` and `buf format -w` to validate proto changes

## 2. Backend — Repository

- [x] 2.1 Add `ListByArtists(ctx, artistIDs []string) ([]*entity.Concert, error)` to `ConcertRepository` interface
- [x] 2.2 Implement `ListByArtists` SQL query with `WHERE c.artist_id = ANY($1)`, JOIN venues including `v.latitude, v.longitude`, ORDER BY `e.local_event_date ASC`
- [x] 2.3 Write integration test for `ListByArtists` verifying multi-artist query and venue coordinate population

## 3. Backend — Use Case

- [x] 3.1 Add `ListWithProximity(ctx, artistIDs []string, home *entity.Home) ([]*entity.ProximityGroup, error)` to concert use case interface
- [x] 3.2 Implement `ListWithProximity`: resolve centroid from `home.Level1` via `geo.ResolveCentroid()`, call `repo.ListByArtists()`, then `entity.GroupByDateAndProximity()`
- [x] 3.3 Write unit test for `ListWithProximity` with mocked repository

## 4. Backend — RPC Handler

- [x] 4.1 Add `ListWithProximity` handler to `ConcertHandler` mapping proto request to use case call
- [x] 4.2 Register `ListWithProximity` in Wire provider set (not needed — Connect auto-discovers methods on handler struct)
- [x] 4.3 Run `mockery` to regenerate mocks for updated interface

## 5. Frontend — Coach Mark Fix

- [x] 5.1 Fix `laneIntroSelector` getter in `dashboard-route.ts`: change `[data-stage-home]` → `[data-stage="home"]`, `[data-stage-near]` → `[data-stage="near"]`, `[data-stage-away]` → `[data-stage="away"]`
- [x] 5.2 Add `this.cleanup()` call at the start of `findAndHighlight()` in `coach-mark.ts` to cancel pending retry timers

## 6. Frontend — ListWithProximity Integration

- [x] 6.1 Replace `listByFollowerOnboarding()` in `concert-service.ts`: call `ListWithProximity` RPC with guest's `followed artist IDs` + `Home` instead of N individual `List` calls
- [x] 6.2 Remove `groupConcertsByDate()` helper function (no longer needed — server returns ProximityGroups)

## 7. Verification

- [ ] 7.1 Run `make check` in backend (blocked: handler references BSR-generated types not yet available)
- [ ] 7.2 Run `make check` in frontend (blocked: imports BSR-generated types not yet available)
- [ ] 7.3 Manual E2E: verify onboarding flow from discovery → dashboard → stage spotlights → concert card → my-artists
