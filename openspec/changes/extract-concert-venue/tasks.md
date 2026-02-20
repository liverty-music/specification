## 1. Entity Layer

- [ ] 1.1 Rename `ScrapedConcert.VenueName` → `ListedVenueName` in `internal/entity/concert.go`
- [ ] 1.2 Add `AdminArea *string` field to `ScrapedConcert` in `internal/entity/concert.go`
- [ ] 1.3 Add `AdminArea *string` field to `Venue` in `internal/entity/venue.go`
- [ ] 1.4 Add `ListedVenueName string` field to `Event` in `internal/entity/event.go`

## 2. Gemini Extraction

- [ ] 2.1 Add `admin_area` field to `eventSchema` in `internal/infrastructure/gcp/gemini/searcher.go` (optional, not in `Required`)
- [ ] 2.2 Add `AdminArea *string` to `ScrapedEvent` struct
- [ ] 2.3 Update `promptTemplate` to instruct extraction of `admin_area` with "confident or empty" rule
- [ ] 2.4 Update `parseEvents()` to rename `ev.Venue` → `ev.ListedVenueName` and map `ev.AdminArea` to `ScrapedConcert`

## 3. Database Migration

- [ ] 3.1 Create new migration file adding `admin_area TEXT` column to `venues` table
- [ ] 3.2 Add `listed_venue_name TEXT` column to `events` table in the same migration
- [ ] 3.3 Update `schema.sql` to reflect the new columns

## 4. Repository

- [ ] 4.1 Update `insertVenueQuery` in `internal/infrastructure/database/rdb/venue_repo.go` to include `admin_area`
- [ ] 4.2 Update `getVenueQuery` and `getVenueByNameQuery` to SELECT `admin_area`
- [ ] 4.3 Update `Create()`, `Get()`, `GetByName()` Scan/Exec calls to include `AdminArea`

## 5. Use Case

- [ ] 5.1 Update `concert_uc.go` to use `s.ListedVenueName` (renamed from `s.VenueName`) for venue lookup/creation key
- [ ] 5.2 Pass `AdminArea: s.AdminArea` when constructing `entity.Venue`
- [ ] 5.3 Pass `ListedVenueName: s.ListedVenueName` when constructing `entity.Event`

## 6. Proto & Mapper

- [ ] 6.1 Add `string admin_area = 3` field to `Venue` message in `proto/liverty_music/entity/v1/venue.proto`
- [ ] 6.2 Update `VenueToProto()` in `internal/adapter/rpc/mapper/concert.go` to map `AdminArea`

## 7. Tests

- [ ] 7.1 Update `concert_uc_test.go`: rename all `VenueName` → `ListedVenueName` in `ScrapedConcert` literals
- [ ] 7.2 Add test cases in `concert_uc_test.go` for `AdminArea` being stored on new venue creation
- [ ] 7.3 Update `venue_repo_test.go` to include `AdminArea` field in test fixtures and assertions
- [ ] 7.4 Update `searcher_test.go` (unit + integration) for new `admin_area` field in JSON schema and `ScrapedConcert` output
