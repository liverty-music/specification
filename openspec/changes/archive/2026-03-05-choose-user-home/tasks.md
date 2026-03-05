## 1. Create Unified Component

- [x] 1.1 Create `frontend/src/components/user-home-selector/user-home-selector.ts` with `UserHomeSelector` class, 2-step state management (Step 1: regions + quick-select, Step 2: prefectures), `@bindable onHomeSelected` callback, and persistence logic (RPC for authenticated, localStorage for guest)
- [x] 1.2 Create `frontend/src/components/user-home-selector/user-home-selector.html` with BottomSheet dialog template: Step 1 view (quick-select city buttons + region buttons), Step 2 view (back button + prefecture list), conditional rendering via `selectedRegion` state
- [x] 1.3 Create `frontend/src/components/user-home-selector/user-home-selector.css` with BottomSheet dialog styles: slide-up animation, backdrop blur, prefers-reduced-motion support, dark surface palette tokens
- [x] 1.4 Add static `getStoredHome()` method on `UserHomeSelector` that reads from `localStorage` using `StorageKeys.guestHome`

## 2. i18n Key Migration

- [x] 2.1 Add `userHome.*` namespace to `frontend/src/locales/en/translation.json` with keys: `title`, `description`, `quickSelect`, `selectByRegion`, `back`, plus nested `regions.*`, `prefectures.*`, `cities.*`
- [x] 2.2 Add `userHome.*` namespace to `frontend/src/locales/ja/translation.json` with equivalent Japanese translations
- [x] 2.3 Remove old `region.*` and `areaSelector.*` keys from both locale files
- [x] 2.4 Rename `settings.myArea` to `settings.myHomeArea` in both locale files
- [x] 2.5 Rename `dashboard.header.myCity` to `dashboard.header.homeArea` in both locale files

## 3. Integration Points

- [x] 3.1 Update `frontend/src/routes/dashboard.ts` and `dashboard.html` to use `<user-home-selector>` instead of `<region-setup-sheet>`, bind `onHomeSelected` callback, replace `RegionSetupSheet.getStoredRegion()` with `UserHomeSelector.getStoredHome()`
- [x] 3.2 Update `frontend/src/routes/settings/settings-page.ts` and `settings-page.html` to use `<user-home-selector>` instead of `<area-selector-sheet>`, bind `onHomeSelected` callback, replace `AreaSelectorSheet.getStoredArea()` with `UserHomeSelector.getStoredHome()`
- [x] 3.3 Update any other references to `RegionSetupSheet` or `AreaSelectorSheet` (grep for imports, DI registrations in `main.ts` or component registrations)

## 4. Cleanup

- [x] 4.1 Delete `frontend/src/components/region-setup-sheet/` directory (ts, html, css)
- [x] 4.2 Delete `frontend/src/components/area-selector-sheet/` directory (ts, html, css)
- [x] 4.3 Grep codebase for orphaned references to old component names, i18n keys (`region.title`, `region.description`, `region.majorCities`, `region.selectByPrefecture`, `areaSelector.*`), and old method names (`getStoredRegion`, `getStoredArea`, `onRegionSelected`, `onAreaSelected`)

## 5. Verification

- [x] 5.1 Run `make check` in frontend (Biome lint + format + typecheck + unit tests)
- [x] 5.2 Manually verify onboarding flow: Dashboard BottomSheet opens with 2-step selector, quick-select works, region->prefecture works
- [x] 5.3 Manually verify settings flow: Settings "My Home Area" row opens same selector, selection updates display
