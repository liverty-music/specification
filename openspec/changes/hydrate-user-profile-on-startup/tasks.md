## 1. UserService state extension

- [x] 1.1 Add `_current: User | undefined` private field and `current` public getter to `UserServiceClient`
- [x] 1.2 Add `ensureLoaded(): Promise<User | undefined>` method — if `_current` is not undefined, return it; if not authenticated, return undefined; otherwise call `get({})` RPC and store result in `_current`
- [x] 1.3 Add `clear()` method that sets `_current = undefined`
- [x] 1.4 Update `updateHome()` to set `_current` from the RPC response (`resp.user`)

## 2. App startup hydration

- [x] 2.1 Register `AppTask.activating()` in `main.ts` that awaits `authService.ready`, then calls `userService.ensureLoaded()` if authenticated

## 3. Auth callback integration

- [x] 3.1 Add `await userService.ensureLoaded()` in `auth-callback.ts` after `provisionUser()` for both sign-in and sign-up paths

## 4. Consumer updates

- [x] 4.1 Update `SettingsPage.loading()` to read home from `userService.current?.home` with guest localStorage fallback
- [x] 4.2 Update `Dashboard.loading()` to read `needsRegion` from `userService.current?.home` instead of calling `get({})` directly, with guest localStorage fallback
- [x] 4.3 Remove the standalone `UserService.Get` call in `Dashboard.loading()` (replaced by centralized hydration)

## 5. Sign-out cleanup

- [x] 5.1 Call `userService.clear()` in `SettingsPage.signOut()` before `authService.signOut()`

## 6. Verification

- [x] 6.1 Run `make check` and fix any lint or type errors
- [x] 6.2 Manually verify: sign up flow → Settings shows correct home area
- [x] 6.3 Manually verify: sign in flow → Settings shows correct home area
- [x] 6.4 Manually verify: page reload → Settings still shows correct home area
- [x] 6.5 Manually verify: guest flow → home area still works via localStorage
