## 1. Specification — Proto Schema

- [x] 1.1 Create `proto/liverty_music/entity/v1/geo_location.proto` with `GeoLocation` message (`latitude`, `longitude`, `admin_area`)
- [x] 1.2 Add `ListByLocation` RPC to `proto/liverty_music/rpc/concert/v1/concert_service.proto` with `ListByLocationRequest` / `ListByLocationResponse`; add protovalidate constraint `to - from ≤ 30 days`
- [x] 1.3 Rename `ListWithProximity` → `ListByArtists` in `concert_service.proto` (update request/response message names to match)
- [x] 1.4 Run `buf lint` and `buf format -w`; verify `buf breaking` only flags the intentional rename
- [x] 1.5 Open specification PR, add `buf skip breaking` label for the rename, get review

## 2. Specification — Release

- [x] 2.1 Merge specification PR to main
- [x] 2.2 Publish GitHub Release (tag `vX.Y.Z`) to trigger `buf-release.yml` → BSR gen
- [x] 2.3 Monitor `gh run list --repo liverty-music/specification --workflow buf-release.yml` until BSR gen succeeds

## 3. Backend — Repository Layer

- [x] 3.1 Upgrade backend generated package: `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z && go mod tidy`
- [x] 3.2 Add `ConcertRepository.ListByLocation(ctx, geoLocation, from, to)` method; SQL query: `WHERE e.local_event_date BETWEEN $from AND $to` with bounding-box pre-filter on `v.latitude/longitude` + `v.admin_area = $admin_area` OR clause
- [x] 3.3 Apply final Haversine 200 km filter in Go via `Concert.ProximityTo`; since that method takes `*entity.Home`, construct a transient adapter: `entity.Home{Level1: req.AdminArea, Centroid: &entity.Coordinates{Latitude: req.Latitude, Longitude: req.Longitude}}`; pass it to `entity.GroupByDateAndProximity`; strip ProximityGroup entries where `len(g.Home)+len(g.Nearby)==0` (entire empty-lane date rows must be omitted, not returned)

## 4. Backend — Use Case & Handler

- [x] 4.1 Add `ConcertUseCase.ListByLocation(ctx, geoLocation, from, to)` method; call `ConcertRepository.ListByLocation`; construct transient `*entity.Home` from `geoLocation` fields (per task 3.3); call `entity.GroupByDateAndProximity(concerts, adaptedHome)`; strip ProximityGroup entries where `len(g.Home)+len(g.Nearby)==0` before returning
- [x] 4.2 Add `ListByLocation` handler in `internal/adapter/rpc/concert_handler.go`; map `entity.v1.GeoLocation` proto to `entity.GeoLocation` Go struct; no auth required
- [x] 4.3 Rename `ListWithProximity` handler to `ListByArtists`; update DI wiring
- [x] 4.4 Add unit tests for `ConcertUseCase.ListByLocation` (mock repo; verify AWAY exclusion and correct GroupByDateAndProximity call)
- [x] 4.5 Run `make check` — all tests green

## 5. Backend — PR

- [x] 5.1 Open backend PR; ensure CI passes (govulncheck, schema-lint, tests)
- [x] 5.2 Merge backend PR; verify deployment via `gh run list --repo liverty-music/backend --branch main`

## 6. Frontend — Dependency & Centroid Constants

- [x] 6.1 Upgrade frontend generated package: `npm install @buf/liverty-music_schema.connectrpc_es@latest`
- [x] 6.2 Rename `listWithProximity` → `listByArtists` in all frontend call sites: `src/services/concert-store.ts` (public method + all internal usages), `src/adapter/rpc/client/concert-client.ts`, and `src/routes/welcome/welcome-route.ts`
- [x] 6.3 Add `JP_PREFECTURE_CENTROIDS` constant map (`Record<string, { lat: number; lng: number }>`) for all 47 JP prefectures to `src/entities/user.ts` alongside `JP_PREFECTURES` (same file, same key space — single source of truth)
- [x] 6.4 Add helper `geoLocationFromLevel1(level1: string): GeoLocation` that looks up `JP_PREFECTURE_CENTROIDS` and returns a `GeoLocation` proto object (`{ latitude, longitude, adminArea: level1 }`)

## 7. Frontend — UserHomeSelector Refactor

- [x] 7.1 Remove `IUserStore` and `IAuthService` injection from `UserHomeSelector`; remove any internal `updateHome()` / localStorage write calls
- [x] 7.2 Add `@bindable currentCode: string | null` prop to `UserHomeSelector`; replace the former `currentHomeCode` getter (which derived from `userStore.currentHome`) with this bindable; use `currentCode` to drive the active-highlight state on prefecture / city buttons
- [x] 7.3 Ensure `onHomeSelected(code: string)` is the sole output of the component
- [x] 7.4 Update Settings page: pass `currentCode.bind="userStore.currentHome"` to `user-home-selector`; in `onHomeSelected` handler call `userStore.updateHome(code)` for authenticated users, write `guest.home` to localStorage for guests
- [x] 7.5 Update onboarding flow with same persistence logic and `currentCode` binding
- [x] 7.6 Run `make check` — no type errors, existing E2E smoke tests green

## 8. Frontend — Dashboard Toggle & All Nearby Mode

- [x] 8.1 Add mode toggle ("My Timetable" / "All Nearby") to `dashboard-route.html` / `dashboard-route.ts`; default to My Timetable; session-only state (not persisted)
- [x] 8.2 Show date-preset selector and area selector only when All Nearby mode is active
- [x] 8.3 Implement date-preset selector component (今週末 / 7日以内 / 30日以内 / カスタム) with `LocalDate` pair output; implement 今週末 date logic (Sat–Sun relative to today)
- [x] 8.4 Implement area selector: display current area name; open `user-home-selector` on tap passing `currentCode.bind="selectedAreaCode ?? userStore.currentHome"`; on `onHomeSelected` update route-local `selectedAreaCode` state; do NOT call `userStore.updateHome()`; resolve `GeoLocation` from `selectedAreaCode` via `geoLocationFromLevel1()` (override case) or from `user.home.centroid.latitude/longitude` + `user.home.level_1` (default case)
- [x] 8.5 Wire `ConcertStore.listByLocation(geoLocation, from, to)` call triggered by mode switch or filter change; cache result in route-local state separate from My Timetable cache

## 9. Frontend — All Nearby Concert List UI

- [x] 9.1 Pass All Nearby `ProximityGroup[]` to `ConcertHighway`; set `showVenueAlways: true` (or equivalent prop) so venue name renders in HOME lane as well as NEARBY
- [x] 9.2 Add `showVenueAlways` (or `showLocationLabel`) bindable to `ConcertHighway` / `EventCard`; when `true`, render venue label for all lanes; default `false` to preserve My Timetable behavior
- [x] 9.3 Implement empty-state UI for All Nearby mode when no concerts returned; include link to Discovery tab
- [x] 9.4 Add follow CTA to `EventDetailSheet`: (1) inject `IFollowStore`; (2) add `@bindable isAllNearby: boolean` flag (default `false`) to distinguish All Nearby context from My Timetable — show the follow button only when `isAllNearby` is true and `!followStore.isFollowed(event.artistId)`; (3) add null guard on `event.artist` before calling `followStore.follow(artist)` — if `artist` is `undefined` (unresolved performer), log a warning and do not throw; (4) update button to "Following" state without DNA Orb animation; (5) show sign-up prompt banner for unauthenticated users instead of calling follow

## 10. Frontend — PR & Prod Release

- [x] 10.1 Run `make check` — type-check, unit tests, E2E smoke green
- [x] 10.2 Open frontend PR; ensure CI passes
- [x] 10.3 Merge frontend PR
- [x] 10.4 Create frontend GitHub Release → prod pin-bump → verify ArgoCD sync
