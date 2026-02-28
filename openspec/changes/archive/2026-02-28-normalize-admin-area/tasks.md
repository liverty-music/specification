## 1. Proto Definitions (specification repo)

- [x] 1.1 Add `Home` value-object message to `user.proto` with ISO 3166-2 string validation (2–6 chars)
- [x] 1.2 Add `home` field to `User` message in `user.proto`
- [x] 1.3 Add `UpdateHome` RPC, `UpdateHomeRequest`, and `UpdateHomeResponse` to `user_service.proto`
- [x] 1.4 Update `AdminArea` message doc comment in `venue.proto` to specify ISO 3166-2 format
- [x] 1.5 Run `buf lint` and `buf format -w` to validate proto changes

## 2. Admin Area Normalization Package (backend repo)

- [x] 2.1 Create `internal/infrastructure/geo/normalize.go` with `NormalizeAdminArea(text string) *string` function and JP prefecture lookup table (ja/en variants → ISO 3166-2)
- [x] 2.2 Create `internal/infrastructure/geo/normalize_test.go` with table-driven tests covering: Japanese names with/without suffix, English names, case insensitivity, empty/unknown inputs
- [x] 2.3 Create `internal/infrastructure/geo/display.go` with `DisplayName(code string, lang string) string` for ISO code → locale text conversion (used by venue enrichment search hint)
- [x] 2.4 Create `internal/infrastructure/geo/display_test.go`

## 3. Database Migrations (backend repo)

- [x] 3.1 Create migration: `ALTER TABLE users ADD COLUMN home TEXT`
- [x] 3.2 Create migration: Convert existing `venues.admin_area` free-text values to ISO 3166-2 codes using UPDATE with CASE expression; set unrecognized values to NULL

## 4. Backend — User Home (backend repo)

- [x] 4.1 Add `Home *string` field to `entity.User` and `entity.NewUser` structs
- [x] 4.2 Add `UpdateHome(ctx context.Context, id string, home string) (*User, error)` to `entity.UserRepository` interface
- [x] 4.3 Implement `UpdateHome` in `rdb.UserRepository` — UPDATE `users SET home = $2 WHERE id = $1`
- [x] 4.4 Update existing `Create`, `Get`, `GetByExternalID`, `List` queries to include `home` column
- [x] 4.5 Add `UpdateHome` to `usecase.UserUseCase` interface and implementation with ISO 3166-2 validation
- [x] 4.6 Add `UpdateHome` handler to `rpc.UserHandler` — map proto request to use case call
- [x] 4.7 Update `mapper/user.go` to map `Home` field between proto and entity
- [x] 4.8 Register `UpdateHome` route in Connect service registration
- [x] 4.9 Write unit tests for repository, use case, and handler

## 5. Backend — Concert Discovery Pipeline Integration (backend repo)

- [x] 5.1 Wire `geo.NormalizeAdminArea()` into Gemini response post-processing in `searcher.go` `parseEvents()` — normalize `ev.AdminArea` before returning
- [x] 5.2 Update `VenuePlaceSearcher.SearchPlace` callers in MusicBrainz and Google Maps clients to convert ISO code to display text via `geo.DisplayName()` before querying
- [x] 5.3 Update existing tests to use ISO 3166-2 codes in test fixtures

## 6. Frontend — RPC Integration and Lane Rename (frontend repo)

- [x] 6.1 Add `updateHome` method to `UserServiceClient` calling `UserService.UpdateHome`
- [x] 6.2 Update `RegionSetupSheet` to use ISO 3166-2 codes as values and call `updateHome` RPC for authenticated users
- [x] 6.3 Add ISO 3166-2 display name utility (npm package or lookup map) for locale-aware rendering
- [x] 6.4 Update `StorageKeys`: remove `userAdminArea`, rename `guestAdminArea` to `guestHome`; add migration logic for existing localStorage keys
- [x] 6.5 Update `DashboardService.groupByDate` to read home from `User` entity (authenticated) or `guest.home` localStorage (guest)
- [x] 6.6 Rename `assignLane` return values from `main/region/other` to `home/nearby/away`; update comparison to use ISO code equality (remove Japanese suffix strip hack)
- [x] 6.7 Update `live-highway.html` lane labels and grid column references
- [x] 6.8 Update `LiveEvent` interface: rename `adminArea` usage to use ISO codes; update `locationLabel` to use display name conversion
- [x] 6.9 Update `event-detail-sheet.ts` Google Maps URL construction to convert ISO code to text for search query

## 7. Proto — Structured Home & CreateRequest (specification repo)

- [x] 7.1 Restructure `Home` message: replace `string value` with `country_code`, `level_1`, `optional level_2` fields
- [x] 7.2 Add optional `home` field to `CreateRequest` in `user_service.proto`
- [x] 7.3 Run `buf lint` and `buf format -w` to validate proto changes

## 8. Backend — Structured Home Entity & DB (backend repo)

- [x] 8.1 Add `entity.Home` struct with `ID`, `CountryCode`, `Level1`, `Level2 *string` fields; update `entity.User.Home` from `*string` to `*Home`; update `entity.NewUser.Home` similarly
- [x] 8.2 Create DB migration: `CREATE TABLE homes (id, user_id UNIQUE FK, country_code, level_1, level_2)`; add `users.home_id` FK
- [x] 8.3 Update `rdb.UserRepository` queries: all user SELECT queries JOIN `homes`; scan 3 home columns; `Create` inserts into `homes` if home provided; `UpdateHome` uses UPSERT on `homes`
- [x] 8.4 Update `entity.UserRepository` interface: `UpdateHome` signature from `(id, home string)` to `(id string, home *Home)`; `Create` accepts `NewUser` with optional `*Home`
- [x] 8.5 Update `usecase.UserUseCase.UpdateHome` to accept `*entity.Home`; add structured validation (country_code format, level_1 ISO 3166-2, level_1 prefix matches country_code)
- [x] 8.6 Update `mapper/user.go`: `UserToProto` maps structured Home fields; add `ProtoHomeToEntity` helper; update `NewUserFromCreateRequest` to extract optional home from `CreateRequest`
- [x] 8.7 Update `rpc.UserHandler.Create` to extract optional home from request and pass to use case
- [x] 8.8 Update `rpc.UserHandler.UpdateHome` to pass structured `*entity.Home` instead of string
- [x] 8.9 Update unit tests: `user_uc_test.go`, `user_repo_test.go`, `user_handler_test.go` for structured Home

## 9. Frontend — Structured Home RPC (frontend repo)

- [x] 9.1 Add `codeToHome(code: string)` helper to `iso3166.ts` that converts ISO 3166-2 code to `{ countryCode, level1 }` object
- [x] 9.2 Update `UserServiceClient.updateHome` to accept structured Home and send `{ countryCode, level1, level2 }` to RPC
- [x] 9.3 Update `RegionSetupSheet.saveRegion` and `AreaSelectorSheet.selectPrefecture` to use `codeToHome()` when calling `updateHome`
- [x] 9.4 Update `DashboardService.getUserHome` to read `user.home?.level1` instead of `user.home?.value`
- [x] 9.5 Update `auth-callback.ts` `provisionUser` to include guest home in `CreateRequest` using `codeToHome()`
