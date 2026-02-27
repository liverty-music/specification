## 1. Proto Definitions (specification repo)

- [ ] 1.1 Add `Home` value-object message to `user.proto` with ISO 3166-2 string validation (2–6 chars)
- [ ] 1.2 Add `home` field to `User` message in `user.proto`
- [ ] 1.3 Add `UpdateHome` RPC, `UpdateHomeRequest`, and `UpdateHomeResponse` to `user_service.proto`
- [ ] 1.4 Update `AdminArea` message doc comment in `venue.proto` to specify ISO 3166-2 format
- [ ] 1.5 Run `buf lint` and `buf format -w` to validate proto changes

## 2. Admin Area Normalization Package (backend repo)

- [ ] 2.1 Create `internal/infrastructure/geo/normalize.go` with `NormalizeAdminArea(text string) *string` function and JP prefecture lookup table (ja/en variants → ISO 3166-2)
- [ ] 2.2 Create `internal/infrastructure/geo/normalize_test.go` with table-driven tests covering: Japanese names with/without suffix, English names, case insensitivity, empty/unknown inputs
- [ ] 2.3 Create `internal/infrastructure/geo/display.go` with `DisplayName(code string, lang string) string` for ISO code → locale text conversion (used by venue enrichment search hint)
- [ ] 2.4 Create `internal/infrastructure/geo/display_test.go`

## 3. Database Migrations (backend repo)

- [ ] 3.1 Create migration: `ALTER TABLE users ADD COLUMN home TEXT`
- [ ] 3.2 Create migration: Convert existing `venues.admin_area` free-text values to ISO 3166-2 codes using UPDATE with CASE expression; set unrecognized values to NULL

## 4. Backend — User Home (backend repo)

- [ ] 4.1 Add `Home *string` field to `entity.User` and `entity.NewUser` structs
- [ ] 4.2 Add `UpdateHome(ctx context.Context, id string, home string) (*User, error)` to `entity.UserRepository` interface
- [ ] 4.3 Implement `UpdateHome` in `rdb.UserRepository` — UPDATE `users SET home = $2 WHERE id = $1`
- [ ] 4.4 Update existing `Create`, `Get`, `GetByExternalID`, `List` queries to include `home` column
- [ ] 4.5 Add `UpdateHome` to `usecase.UserUseCase` interface and implementation with ISO 3166-2 validation
- [ ] 4.6 Add `UpdateHome` handler to `rpc.UserHandler` — map proto request to use case call
- [ ] 4.7 Update `mapper/user.go` to map `Home` field between proto and entity
- [ ] 4.8 Register `UpdateHome` route in Connect service registration
- [ ] 4.9 Write unit tests for repository, use case, and handler

## 5. Backend — Concert Discovery Pipeline Integration (backend repo)

- [ ] 5.1 Wire `geo.NormalizeAdminArea()` into Gemini response post-processing in `searcher.go` `parseEvents()` — normalize `ev.AdminArea` before returning
- [ ] 5.2 Update `VenuePlaceSearcher.SearchPlace` callers in MusicBrainz and Google Maps clients to convert ISO code to display text via `geo.DisplayName()` before querying
- [ ] 5.3 Update existing tests to use ISO 3166-2 codes in test fixtures

## 6. Frontend — RPC Integration and Lane Rename (frontend repo)

- [ ] 6.1 Add `updateHome` method to `UserServiceClient` calling `UserService.UpdateHome`
- [ ] 6.2 Update `RegionSetupSheet` to use ISO 3166-2 codes as values and call `updateHome` RPC for authenticated users
- [ ] 6.3 Add ISO 3166-2 display name utility (npm package or lookup map) for locale-aware rendering
- [ ] 6.4 Update `StorageKeys`: remove `userAdminArea`, rename `guestAdminArea` to `guestHome`; add migration logic for existing localStorage keys
- [ ] 6.5 Update `DashboardService.groupByDate` to read home from `User` entity (authenticated) or `guest.home` localStorage (guest)
- [ ] 6.6 Rename `assignLane` return values from `main/region/other` to `home/nearby/away`; update comparison to use ISO code equality (remove Japanese suffix strip hack)
- [ ] 6.7 Update `live-highway.html` lane labels and grid column references
- [ ] 6.8 Update `LiveEvent` interface: rename `adminArea` usage to use ISO codes; update `locationLabel` to use display name conversion
- [ ] 6.9 Update `event-detail-sheet.ts` Google Maps URL construction to convert ISO code to text for search query
