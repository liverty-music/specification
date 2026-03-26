## 1. Decompose dashboard-service

- [x] 1.1 Move `protoGroupToDateGroup()` to `concert-service.ts` as public `toDateGroups()` (accepting `ProximityGroup[]` and an artist map)
- [x] 1.2 Move `fetchFollowedArtistMap()` to `follow-service.ts` as public `getFollowedArtistMap()`
- [x] 1.3 Move `fetchJourneyMap()` — kept inline in dashboard-route since it's orchestration logic (auth check + graceful fallback); `listByUser` already exists on RPC client
- [x] 1.4 Inline the `loadDashboardEvents()` orchestration into `dashboard-route.ts` `loadData()`, calling the three domain services directly
- [x] 1.5 Delete `dashboard-service.ts` and remove its DI registration from `main.ts`

## 2. Extract `<concert-highway>` CE

- [x] 2.1 Create `components/live-highway/concert-highway.ts` with `@bindable` API: `dateGroups`, `readonly`, `showBeams`
- [x] 2.2 Create `components/live-highway/concert-highway.html` — move the stage-header, concert-scroll, date-group-list, lane-grid, and beam-overlay markup from `dashboard-route.html`
- [x] 2.3 Create `components/live-highway/concert-highway.css` — move the 3-column grid, laser beam, date-separator, lane-grid, lane, and empty-state styles from `dashboard-route.css`
- [x] 2.4 Move `buildBeamIndexMap()`, `updateBeamPositions()`, `scheduleBeamUpdate()`, and scroll listener setup/teardown from `dashboard-route.ts` into the CE
- [x] 2.5 Export the CE from `components/live-highway/index.ts` (or equivalent barrel)

## 3. Refactor dashboard-route to consume CE

- [x] 3.1 Replace the inline lane-grid/beam HTML in `dashboard-route.html` with `<concert-highway date-groups.bind="dateGroups" event-selected.trigger="onEventSelected($event)">`
- [x] 3.2 Remove the grid/beam/lane CSS from `dashboard-route.css` (now owned by CE)
- [x] 3.3 Remove beam-tracking methods from `dashboard-route.ts` (now owned by CE)
- [x] 3.4 Verify dashboard route still renders correctly — run `make check` and E2E tests

## 4. Rewrite welcome-route to use CE + ListWithProximity

- [x] 4.1 Replace `loadPreviewConcerts()` in `welcome-route.ts` with `loadPreviewData()` that calls `concertService.listWithProximity(PREVIEW_ARTIST_IDS, 'JP', 'JP-13')` and `concertService.toDateGroups()`
- [x] 4.2 Replace the inline lane-grid HTML in `welcome-route.html` with `<concert-highway date-groups.bind="dateGroups" readonly="true">` wrapped in a `.welcome-preview` container
- [x] 4.3 Add Peek Preview CSS to `welcome-route.css`: `.welcome-preview` with `~55svh` fixed height, `overflow-y: scroll`, bottom fade-out gradient mask
- [x] 4.4 Add sticky CTA layout: position CTA buttons and guest-friendly copy below the preview with sticky behavior
- [x] 4.5 Verify welcome page renders the 3-column grid with real concert data — run `make check`

## 5. Cleanup

- [x] 5.1 Remove any unused imports or dead code from dashboard-route, welcome-route, and service files
- [x] 5.2 Run full lint and test suite (`make check`) to verify no regressions
