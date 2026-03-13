## 1. Fix needsRegion for Authenticated Users (Bug 2)

- [x] 1.1 In `dashboard.ts:loading()`, add auth-aware `needsRegion` check: if authenticated, call `UserService.Get` (parallelized with `loadDashboardEvents()`) and set `needsRegion` based on `user.home` presence; if guest, fall back to `UserHomeSelector.getStoredHome()`
- [x] 1.2 Add unit test: authenticated user with `user.home` set → `needsRegion` is `false`, home selector not shown
- [x] 1.3 Add unit test: authenticated user without `user.home` → `needsRegion` is `true`, home selector shown
- [x] 1.4 Add unit test: guest user with `guest.home` in localStorage → `needsRegion` is `false`
- [x] 1.5 Add unit test: guest user without `guest.home` → `needsRegion` is `true`

## 2. Reload Data After Home Selection (Bug 1)

- [x] 2.1 In `dashboard.ts:onHomeSelected()`, call `loadData()` after home is stored (for both onboarding and non-onboarding paths)
- [x] 2.2 Add unit test: `onHomeSelected()` triggers `loadDashboardEvents()` call
- [x] 2.3 Add unit test: after `onHomeSelected()`, `dateGroups` reflects reloaded data

## 3. Verification

- [x] 3.1 Run `make check` in frontend repo — all lint and tests pass
- [x] 3.2 E2E test: onboarding flow — select home area → verify blur removed and data reloaded (`dashboard-lane-classification.spec.ts`)
- [x] 3.3 E2E test: returning user with stored home → verify no home selector shown (`dashboard-lane-classification.spec.ts`)
