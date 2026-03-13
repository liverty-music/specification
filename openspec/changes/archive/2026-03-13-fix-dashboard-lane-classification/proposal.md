## Why

The dashboard timeline displays all concerts in the "Away Stage" lane regardless of the user's home area. Two implementation bugs cause this:

1. **Onboarding data reload gap**: `dashboard.ts:onHomeSelected()` stores the selected home in localStorage and starts the lane intro, but does not re-invoke `loadData()`. The initial load ran before the user selected a home (Home=nil → backend classifies all concerts as Away), and this stale result remains on screen.
2. **Authenticated user home source mismatch**: `needsRegion` is determined solely by `localStorage.getItem('guest.home')` via `UserHomeSelector.getStoredHome()`. After sign-up, `GuestDataMergeService.clearAll()` removes all `guest.*` keys — including `guest.home` — so `needsRegion` evaluates to `true` even though the backend already has the user's home. This violates the `user-home` spec requirement: "Dashboard reads home from User entity" (authenticated users SHALL read home from `UserService.Get`, not localStorage).

## What Changes

- **Fix 1 — Reload data after home selection**: In `dashboard.ts:onHomeSelected()`, call `loadData()` after storing the home so the backend re-classifies concerts with the newly selected home context.
- **Fix 2 — Use backend home for authenticated users**: Change the `needsRegion` determination so authenticated users check the `User.home` field from `UserService.Get` instead of localStorage. `getStoredHome()` remains as the guest-only fallback.

## Capabilities

### Modified Capabilities

- `user-home`: Implementation aligns with existing spec requirement "Dashboard reads home from User entity" and "Guest fallback to localStorage".
- `frontend-onboarding-flow`: Home selection during onboarding triggers dashboard data reload.

### New Capabilities

None.

## Impact

- **Frontend**: `dashboard.ts`, potentially `user-home-selector.ts` or a new dashboard-level home resolution helper
- **Backend**: No changes — `UserService.Get` already returns `User.home`
- **Proto**: No changes
