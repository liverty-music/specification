## 1. Dashboard Route — Filter State & URL Parsing

- [x] 1.1 Add `filteredArtistIds: string[]` as an `@observable` property to `DashboardRoute`
- [x] 1.2 Update `loading(_params, next: RouteNode)` to read `next.queryParams.get('artists')?.split(',').filter(Boolean) ?? []` and assign to `filteredArtistIds`
- [x] 1.3 Add `get filteredDateGroups(): DateGroup[]` computed getter — returns `dateGroups` unchanged when `filteredArtistIds` is empty; otherwise filters each group's `home`/`nearby`/`away` arrays by `artistId` and drops empty groups
- [x] 1.4 Add `updateFilterUrl()` private method using `IHistory.replaceState` to sync URL to `/dashboard` or `/dashboard?artists=id1,id2`
- [x] 1.5 Add `filteredArtistIdsChanged()` change handler that calls `updateFilterUrl()`
- [x] 1.6 Inject `IHistory` into `DashboardRoute`

## 2. Dashboard Route — Onboarding Guard

- [x] 2.1 Suppress reading `?artists` param (keep `filteredArtistIds` empty) when `isOnboarding` is true in `loading()`

## 3. `artist-filter-bar` Component

- [x] 3.1 Create `src/components/artist-filter-bar/artist-filter-bar.ts` with two bindables: `followedArtists: Artist[]` and `selectedIds: string[]` (two-way)
- [x] 3.2 Create `src/components/artist-filter-bar/artist-filter-bar.html` — renders dismissible chips for each selected artist, plus a trigger button (`≡`) to open the bottom sheet
- [x] 3.3 Create `src/components/artist-filter-bar/artist-filter-bar.css` — chip styles (CUBE CSS, `max-width` + `text-overflow: ellipsis`), trigger button styles; follow design-system tokens
- [x] 3.4 Implement bottom sheet markup inside `artist-filter-bar.html` using the existing `bottom-sheet` primitive; list all `followedArtists` as checkboxes pre-selected by `selectedIds`
- [x] 3.5 Implement confirm handler: update `selectedIds` binding and close the sheet
- [x] 3.6 Register `artist-filter-bar` in `main.ts` (global custom element)

## 4. Dashboard Template — Integrate Filter Bar

- [x] 4.1 Change `<concert-highway date-groups.bind="dateGroups">` to `date-groups.bind="filteredDateGroups"` in `dashboard-route.html`
- [x] 4.2 Add `<artist-filter-bar>` inside `<page-header>` slot (or adjacent) with bindings: `followed-artists.bind="followedArtists"` and `selected-ids.two-way="filteredArtistIds"`
- [x] 4.3 Expose `get followedArtists(): Artist[]` getter on `DashboardRoute` from `followService.followedArtists`
- [x] 4.4 Hide/disable the filter bar while `isOnboarding` is true (`if.bind="!isOnboarding"` or `disabled.bind`)

## 5. Tests

- [x] 5.1 Unit test `filteredDateGroups` getter: empty filter returns all groups; single-artist filter returns only matching concerts; filter with unknown ID returns empty groups correctly
- [x] 5.2 Unit test `updateFilterUrl()`: empty `filteredArtistIds` produces `/dashboard`; non-empty produces `/dashboard?artists=id1,id2`
- [x] 5.3 Unit test `loading()` query param parsing: `?artists=id1,id2` sets `filteredArtistIds`; absent param sets empty array; onboarding active ignores param
- [x] 5.4 Component smoke test for `artist-filter-bar`: renders chips for selected IDs; chip dismiss updates `selectedIds`; confirm updates binding

## 6. Verification

- [x] 6.1 Run `make check` (lint + typecheck + unit tests) — all pass
- [ ] 6.2 Manual smoke: navigate to `/dashboard?artists=<realId>` — highway shows only that artist's concerts
- [ ] 6.3 Manual smoke: add/remove artists via UI — chips update, URL updates, highway re-filters
- [ ] 6.4 Manual smoke: reload page with active filter — filter is restored from URL
