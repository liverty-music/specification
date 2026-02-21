## 1. Proto: Shared VO Messages

- [x] 1.1 Add `LocalDate`, `StartTime`, `OpenTime`, `Title`, `SourceUrl`, `ListedVenueName` VO wrapper messages to `entity.proto` (or a new shared file)
- [x] 1.2 Run `buf lint` and verify no style violations

## 2. Proto: Update `concert.proto`

- [x] 2.1 Replace `google.type.Date date` with `LocalDate local_date`
- [x] 2.2 Replace `google.type.TimeOfDay start_time` with `StartTime start_time`
- [x] 2.3 Replace `google.type.TimeOfDay open_time` with `OpenTime open_time`
- [x] 2.4 Replace `ConcertTitle title` with `Title title`
- [x] 2.5 Replace `string source_url` with `SourceUrl source_url`
- [x] 2.6 Add `Venue venue = 9`
- [x] 2.7 Add `ListedVenueName listed_venue_name = 10`
- [ ] 2.8 Run `buf breaking` against previous version and confirm expected breaking changes only

## 3. Proto: Update `event.proto`

- [x] 3.1 Replace `VenueId venue_id` with `Venue venue`
- [x] 3.2 Replace `string title` with `Title title`
- [x] 3.3 Replace `google.type.Date local_event_date` with `LocalDate local_date`
- [x] 3.4 Replace `optional Timestamp start_at` with `StartTime start_time`
- [x] 3.5 Replace `optional Timestamp open_at` with `OpenTime open_time`
- [x] 3.6 Remove `create_time` and `update_time` fields
- [x] 3.7 Run `buf lint` to verify

## 4. Proto: Publish to BSR

- [ ] 4.1 Bump schema version (breaking change — semver major)
- [ ] 4.2 Push updated proto to BSR
- [ ] 4.3 Regenerate Go and TypeScript clients from BSR in backend and frontend repos

## 5. Backend: Go Entity

- [ ] 5.1 Rename `entity.Event.LocalEventDate` → `LocalDate` in [internal/entity/event.go](internal/entity/event.go)
- [ ] 5.2 Update all references to `LocalEventDate` in backend (repo, mapper, use case, tests)

## 6. Backend: Repository

- [ ] 6.1 Extend `listConcertsByArtistQuery` and `listUpcomingConcertsByArtistQuery` in [internal/infrastructure/database/rdb/concert_repo.go](internal/infrastructure/database/rdb/concert_repo.go) to JOIN `venues` and SELECT `v.name`, `v.admin_area`
- [ ] 6.2 Add `Venue` struct (or reuse `entity.Venue`) scan target in `ListByArtist`
- [ ] 6.3 Populate `entity.Concert` with resolved `Venue` after scan

## 7. Backend: Mapper

- [ ] 7.1 Update `ConcertToProto` in [internal/adapter/rpc/mapper/concert.go](internal/adapter/rpc/mapper/concert.go) to populate `Venue`, `ListedVenueName`, and updated VO fields
- [ ] 7.2 Remove `TimeToTimeOfDayProto` (now dead code) from mapper
- [ ] 7.3 Update `VenueToProto` if needed for new field types

## 8. Backend: Verification

- [ ] 8.1 Run `go vet ./...` and `golangci-lint run`
- [ ] 8.2 Run existing tests; fix any breakage from entity rename and proto changes

## 9. Frontend: Data Layer

- [ ] 9.1 Update `LiveEvent` interface in [src/components/live-highway/live-event.ts](src/components/live-highway/live-event.ts) — add `adminArea?: string`, fix `venueName` source
- [ ] 9.2 Update `concertToLiveEvent` in [src/services/dashboard-service.ts](src/services/dashboard-service.ts) — map `concert.listedVenueName` → `venueName`, `concert.venue.adminArea` → `adminArea`; remove `'Venue TBD'` hardcode
- [ ] 9.3 Implement lane assignment in `groupByDate` — compare `event.adminArea` vs `RegionSetupSheet.getStoredRegion()`

## 10. Frontend: Concert Detail URL Sync

- [ ] 10.1 Add `/concerts/:id` route configuration to Aurelia router (no new page component needed — handled by sheet)
- [ ] 10.2 Update `EventDetailSheet.open()` to push `/concerts/:id` to router history
- [ ] 10.3 Update `EventDetailSheet.close()` to restore previous URL (dashboard)

## 11. Frontend: Event Detail Sheet — Venue & Maps

- [ ] 11.1 Update `googleMapsUrl` getter in [src/components/live-highway/event-detail-sheet.ts](src/components/live-highway/event-detail-sheet.ts) to include `adminArea` in query when available
- [ ] 11.2 Update sheet template to show `adminArea` below venue name if present
