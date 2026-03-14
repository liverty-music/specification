## Why

After account creation or sign-in, the frontend never fetches the backend User entity at startup. Each page independently decides how to obtain user data — Dashboard calls `UserService.Get` but discards the result after a boolean check, while Settings reads only from `localStorage('guest.home')`. This means authenticated users see "Not set" for My Home Area on the Settings page despite having a home registered in the backend. The root cause is the absence of a centralized user profile hydration step after authentication.

## What Changes

- Add a `current: User | undefined` state field to `UserService` (singleton) to hold the authenticated user's backend profile.
- Add an `ensureLoaded()` method that fetches via `UserService.Get` RPC if `current` is undefined and the user is authenticated (lazy, idempotent).
- Register an `AppTask.activating()` hook in `main.ts` that awaits `authService.ready` and then calls `userService.ensureLoaded()` — ensuring the profile is available before any route renders on page load / reload.
- Call `userService.ensureLoaded()` in `auth-callback.ts` after `provisionUser()` — covering the sign-in and sign-up paths where `AppTask` has already fired.
- Update `UserService.updateHome()` to also update `current` in-memory after a successful RPC, eliminating localStorage as the source of truth for authenticated users.
- Update `SettingsPage.loading()` and `Dashboard.loading()` to read home from `userService.current?.home` instead of localStorage, with a guest fallback.
- Clear `userService.current` on sign-out.

## Capabilities

### New Capabilities

- `user-profile-hydration`: Centralized loading and caching of the authenticated user's backend profile in the frontend, triggered at app startup and after auth callback.

### Modified Capabilities

- `user-home`: The frontend home area persistence spec requires a new scenario — Settings and Dashboard SHALL read home from the hydrated User entity, not localStorage, for authenticated users.
- `settings`: The Settings page requirement for My Home Area display must source from the backend User entity via `UserService` state rather than localStorage.

## Impact

- **Frontend only** — no backend or protobuf changes required. `UserService.Get` RPC already exists and returns `User.home`.
- **Files affected**: `services/user-service.ts`, `main.ts`, `routes/auth-callback.ts`, `routes/settings/settings-page.ts`, `routes/dashboard.ts`.
- **Risk**: Low. The `ensureLoaded()` pattern is idempotent and adds a single RPC call on startup (~50ms). Guest flow is unchanged (localStorage fallback).
